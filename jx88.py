#!/bin/env python3
# -*- coding: utf-8 -*

# cron 0 59 23 * * 0
# export jx88_pins=["pt_pin1","pt_pin2"]

from urllib.parse import unquote, quote
import time, datetime, os, sys
import requests, json, re, random
import threading

UserAgent = ''
script_name = '京喜88助力开红包'


def printT(msg):
    print("[{}]: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg))
    sys.stdout.flush()


def delEnvs(label):
    try:
        if label == 'True' or label == 'yes' or label == 'true' or label == 'Yes':
            return True
        elif label == 'False' or label == 'no' or label == 'false' or label == 'No':
            return False
    except:
        pass
    try:
        if '.' in label:
            return float(label)
        elif '&' in label:
            return label.split('&')
        elif '@' in label:
            return label.split('@')
        else:
            return int(label)
    except:
        return label


class getJDCookie():
    # 适配青龙平台环境ck
    def getckfile(self):
        ql_new = '/ql/config/env.sh'
        ql_old = '/ql/config/cookie.sh'
        if os.path.exists(ql_new):
            printT("当前环境青龙面板新版")
            return ql_new
        elif os.path.exists(ql_old):
            printT("当前环境青龙面板旧版")
            return ql_old

    # 获取cookie
    def getallCookie(self):
        cookies = ''
        ckfile = self.getckfile()
        try:
            if os.path.exists(ckfile):
                with open(ckfile, "r", encoding="utf-8") as f:
                    cks_text = f.read()
                if 'pt_key=' in cks_text and 'pt_pin=' in cks_text:
                    r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
                    cks_list = r.findall(cks_text)
                    if len(cks_list) > 0:
                        for ck in cks_list:
                            cookies += ck
            return cookies
        except Exception as e:
            printT(f"【getCookie Error】{e}")

    # 检测cookie格式是否正确
    def getUserInfo(self, ck, user_order, pinName):
        url = 'https://me-api.jd.com/user_new/info/GetJDUserInfoUnion?orgFlag=JD_PinGou_New&callSource=mainorder&channel=4&isHomewhite=0&sceneval=2&sceneval=2&callback='
        headers = {
            'Cookie': ck,
            'Accept': '*/*',
            'Connection': 'close',
            'Referer': 'https://home.m.jd.com/myJd/home.action',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'me-api.jd.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'zh-cn'
        }
        try:
            resp = requests.get(url=url, headers=headers, timeout=60).json()
            if resp['retcode'] == "0":
                nickname = resp['data']['userInfo']['baseInfo']['nickname']
                return ck, nickname
            else:
                context = f"账号{user_order}【{pinName}】Cookie 已失效！请重新获取。"
                print(context)
                return ck, False
        except Exception:
            context = f"账号{user_order}【{pinName}】Cookie 已失效！请重新获取。"
            print(context)
            return ck, False

    def getcookies(self):
        """
        :return: cookiesList,userNameList,pinNameList
        """
        cookiesList = []
        pinNameList = []
        nickNameList = []
        cookies = self.getallCookie()
        if 'pt_key=' in cookies and 'pt_pin=' in cookies:
            r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
            result = r.findall(cookies)
            if len(result) >= 1:
                printT("您已配置{}个账号".format(len(result)))
                user_order = 1
                for ck in result:
                    r = re.compile(r"pt_pin=(.*?);")
                    pinName = r.findall(ck)
                    pinName = unquote(pinName[0])
                    # 获取账号名
                    ck, nickname = self.getUserInfo(ck, user_order, pinName)
                    if nickname != False:
                        cookiesList.append(ck)
                        pinNameList.append(pinName)
                        nickNameList.append(nickname)
                        user_order += 1
                    else:
                        user_order += 1
                        continue
                if len(cookiesList) > 0:
                    return cookiesList, pinNameList, nickNameList
                else:
                    printT("没有可用Cookie，已退出")
                    exit(4)
        else:
            printT("没有可用Cookie，已退出")
            exit(4)


def getPinEnvs():
    if "jx88_pins" in os.environ:
        if len(os.environ["jx88_pins"]) != 0:
            jx88_pins = os.environ["jx88_pins"]
            jx88_pins = jx88_pins.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(',')
            printT(f"已获取并使用Env环境 jx88_pins:{jx88_pins}")
            return jx88_pins
        else:
            printT('请先配置export jx88_pins=["pt_pin1","pt_pin2"]')
            exit(4)
    printT('请先配置export jx88_pins=["pt_pin1","pt_pin2"]')
    exit(4)

# 随机UA
def userAgent():
    """
    随机生成一个UA
    :return: jdapp;iPhone;9.4.8;14.3;xxxx;network/wifi;ADID/201EDE7F-5111-49E8-9F0D-CCF9677CD6FE;supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone13,4;addressid/2455696156;supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1
    """
    if not UserAgent:
        uuid = ''.join(random.sample('123456789abcdef123456789abcdef123456789abcdef123456789abcdef', 40))
        addressid = ''.join(random.sample('1234567898647', 10))
        iosVer = ''.join(
            random.sample(["14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1", "13.7", "13.1.2", "13.1.1"], 1))
        iosV = iosVer.replace('.', '_')
        iPhone = ''.join(random.sample(["8", "9", "10", "11", "12", "13"], 1))
        ADID = ''.join(random.sample('0987654321ABCDEF', 8)) + '-' + ''.join(
            random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(
            random.sample('0987654321ABCDEF', 4)) + '-' + ''.join(random.sample('0987654321ABCDEF', 12))

        return f'jdapp;iPhone;10.0.4;{iosVer};{uuid};network/wifi;ADID/{ADID};supportApplePay/0;hasUPPay/0;hasOCPay/0;model/iPhone{iPhone},1;addressid/{addressid};supportBestPay/0;appBuild/167629;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS {iosV} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'
    else:
        return UserAgent


# 设置请求头
def setHeaders(cookie):
    headers = {
        "Host": "api.m.jd.com",
        "cookie": cookie,
        "charset": "UTF-8",
        "accept-encoding": "br,gzip,deflate",
        "user-agent": "okhttp/3.12.1;jdmall;android;version/10.0.8;build/89053;screen/1080x2029;os/10;network/wifi;",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset\u003dUTF-8",
        "content-length": "48"
    }
    return headers


# 参与活动
def joinActive(mycookie):
    url = 'https://wq.jd.com/cubeactive/steprewardv3/JoinActive?activeId=489177&publishFlag=1&channel=7&sceneval=2&g_login_type=1&timestamp=' + str(int(time.time())) + '&_=' + str(int(time.time()) + 2) + '&_ste=1'
    UA=userAgent()
    headers = {
        'Host': 'wq.jd.com',
        'Cookie': mycookie,
        'accept': "*/*",
        'user-agent': UA,
        'accept-language': 'zh-cn',
        'referer': 'https://wqactive.jd.com/cube/front/activePublish/step_reward/489177.html?aid=489177'
    }
    res = requests.get(url=url, headers=headers).json()
    # print(res)

def getUserInfo(mycookie):
    invite = ''
    url = 'https://wq.jd.com/cubeactive/steprewardv3/GetUserInfo?activeId=489177&joinDate=' + str(datetime.date.today().strftime('%Y%m%d')) + '&publishFlag=1&channel=7&sceneval=2&g_login_type=1&timestamp=' + str(int(time.time())) + '&_=' + str(int(time.time()) + 2) + '&_ste=1'
    UA = userAgent()
    headers = {
        'Host': 'wq.jd.com',
        'Cookie': mycookie,
        'accept': "*/*",
        'user-agent': UA,
        'accept-language': 'zh-cn',
        'referer': 'https://wqactive.jd.com/cube/front/activePublish/step_reward/489177.html?aid=489177'
    }
    res = requests.get(url=url, headers=headers).json()
    # print(res)
    if res['iRet'] == 0:
        strPin = res['Data']['strUserPin']
        # print(strPin)

    return strPin

# 助力好友
def help(mycookie,nickname,cookiesList,nickNameList):
    joinActive(mycookie)
    strPin = getUserInfo(mycookie)
    UA = userAgent()
    url = 'https://wq.jd.com/cubeactive/steprewardv3/EnrollFriend?activeId=489177&publishFlag=1&channel=7&stepreward_jstoken=fa73cdbbc05b684d372d66a6643df231&timestamp=' + str(int(time.time()) * 1000) + '&phoneid=dc52285fa836e8fb&joinDate=' + str(int(time.time())) + '&strPin=' + strPin + '&_stk=activeId%2Cchannel%2CjoinDate%2Cphoneid%2CpublishFlag%2Cstepreward_jstoken%2CstrPin%2Ctimestamp&_ste=1&h5st=20210806133001545%3B5238589016270447%3B10010%3Btk01w9f821bbaa8nR1RGdUhaRE4xjZXdls9DDWGKwz8Q%2B5f3AlTgTWrTYFTYA1l%2Fku7%2BFdKaaHmdnrTp7RkalOQG68g9%3Be999e97f263e773be9a644982c07c1b5f76e3b513bcb7f67a09be5215ee47e83&_=' + str(int(time.time()) * 1000 + 2) + '&sceneval=2&g_login_type=1&callback=jsonpCBKI&g_ty=ls'
    for i in range(len(cookiesList)):
        headers = {
            'Host': 'wq.jd.com',
            'Cookie': cookiesList[i],
            'accept': "*/*",
            'user-agent': UA,
            'accept-language': 'zh-cn',
            'referer': 'https://wqactive.jd.com/cube/front/activePublish/step_reward/489177.html?aid=489177'
        }
        res_text = requests.get(url=url, headers=headers).text
        try:
            ex = '"sErrMsg":"(.*?)"}'
            res = re.findall(ex, res_text, re.S)
            if len(res) !=0:
                print(nickNameList[i]+'助力'+nickname+'：'+res[0])
        except:
            pass
        time.sleep(1)

    pass

def use_thread(jx88_cookies,nicks, cookiesList,nickNameList):
    threads = []
    for i in range(len(jx88_cookies)):
        threads.append(
            threading.Thread(target=help, args=(jx88_cookies[i], nicks[i],cookiesList,nickNameList))
        )
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def start():
    printT("############{}##########".format(script_name))
    jx88_pins = getPinEnvs()
    get_jd_cookie = getJDCookie()
    cookiesList, pinNameList, nickNameList = get_jd_cookie.getcookies()
    jx88_cookies = []
    nicks = []
    for ckname in jx88_pins:
        try:
            ckNum = pinNameList.index(ckname)
            jx88_cookies.append(cookiesList[ckNum])
            nicks.append(nickNameList[ckNum])
        except Exception as e:
            try:
                ckNum = pinNameList.index(unquote(ckname))
                jx88_cookies.append(cookiesList[ckNum])
                nicks.append(nickNameList[ckNum])
            except:
                print(f"请检查被助力账号【{ckname}】名称是否正确？ck是否存在？提示：助力名字可填pt_pin的值、也可以填账号名。")
                continue
    if len(jx88_cookies) == 0:
        exit(4)
    use_thread(jx88_cookies,nicks, cookiesList,nickNameList)

if __name__ == '__main__':
    start()
