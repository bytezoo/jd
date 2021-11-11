#!/bin/env python3
# -*- coding: utf-8 -*

# cron 0 0 0 * * *
#只做助力和领助力奖励
# export park_pins=["pt_pin1","pt_pin2"]

from urllib.parse import unquote, quote
import time, datetime, os, sys
import requests, json, re, random
import threading,math

linkId = 'LsQNxL7iWDlXUs6cFl-AAg'

UserAgent = ''
script_name = '汪汪乐园助力'

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
            'User-Agent': Ua(),
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
                    cookiesList.append(ck)
                    pinNameList.append(pinName)
                    # ck, nickname = self.getUserInfo(ck, user_order, pinName)
                    # if nickname != False:
                    #     cookiesList.append(ck)
                    #     pinNameList.append(pinName)
                    #     nickNameList.append(nickname)
                    #     user_order += 1
                    # else:
                    #     user_order += 1
                    #     continue
                if len(cookiesList) > 0:
                    return cookiesList, pinNameList
                else:
                    printT("没有可用Cookie，已退出")
                    exit(4)
        else:
            printT("没有可用Cookie，已退出")
            exit(4)

def getPinEnvs():
    if "park_pins" in os.environ:
        if len(os.environ["park_pins"]) != 0:
            park_pins = os.environ["park_pins"]
            park_pins = park_pins.replace('[', '').replace(']', '').replace('\'', '').replace(' ', '').split(',')
            printT(f"已获取并使用Env环境 park_pins:{park_pins}")
            return park_pins
        else:
            printT('请先配置export park_pins=["pt_pin1","pt_pin2"]')
            exit(4)
    printT('请先配置export park_pins=["pt_pin1","pt_pin2"]')
    exit(4)

def randomString(e):
    t = "0123456789abcdef"
    a = len(t)
    n = ""
    for i in range(e):
        n = n + t[math.floor(random.random() * a)]
    return n


def Ua():
    UA = f'jdapp;iPhone;10.2.0;13.1.2;{randomString(40)};M/5.0;network/wifi;ADID/;model/iPhone8,1;addressid/2308460611;appBuild/167853;jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS 13_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1;'
    return UA
def res_post(cookie, body,functionId):
    url = "https://api.m.jd.com/api"
    headers = {
        "Host": "api.m.jd.com",
        "content-length": "150",
        "accept": "application/json, text/plain, */*",
        "origin": "https://joypark.jd.com",
        "user-agent": Ua(),
        "content-type": "application/x-www-form-urlencoded",
        "referer": "https://joypark.jd.com/?activityId\u003dLsQNxL7iWDlXUs6cFl-AAg\u0026sid\u003dc2a66a2aeb6cbac967c1d3484e87bc9w\u0026un_area\u003d2_2830_51806_0",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,en-US;q\u003d0.9",
        "cookie": cookie,
        "x-requested-with": "com.jd.jdlite"
    }
    body = json.dumps(body)
    t = str(int(time.time() * 1000))
    data = {
        'functionId': functionId,
        'body': body,
        '_t': t,
        'appid': 'activities_platform'
    }
    res = requests.post(url=url, headers=headers, data=data).json()
    return res


def get_invitePin(cookie):
    body = {"taskId": "", "inviteType": "", "inviterPin": "", "linkId": linkId}
    try:
        res = res_post(cookie, body,'joyBaseInfo')
        # print(res)
        if res['code'] == 0 and res['errMsg'] == 'success':
            # print(res['data']['invitePin'])
            return res['data']['invitePin']
    except:
        return -1

def get_reward(cookie,park_pin):
    body = {"taskType": "SHARE_INVITE", "taskId": "430", "linkId": linkId}
    while True:
        try:
            res = res_post(cookie, body, 'apTaskDrawAward')
            # print(res)
            if res['success'] == False and '领取次数不足' in res['errMsg']:
                print('---------------------'+park_pin+'领取互助奖励完毕!')
                break
        except:
            break

def help(mycookie, park_pin, cookiesList, pinNameList):
    inviterPin = get_invitePin(mycookie)
    if inviterPin != -1:
        body = {"taskId": "430", "inviteType": "1", "inviterPin": inviterPin, "linkId": linkId}
        for i in range(len(cookiesList)):
            try:
                res = res_post(cookiesList[i],body,'joyBaseInfo')
                # print(res)
                if res['code'] == 0 and res['errMsg'] == 'success':
                    if res['data']['helpState'] == 1:
                        print('【'+pinNameList[i]+'助力'+park_pin+'】：'+'助力成功！')
                    elif res['data']['helpState'] == 0:
                        print('【'+pinNameList[i]+'助力'+park_pin+'】：'+'自己不能助力自己！')
                    elif res['data']['helpState'] == 2:
                        print('【'+pinNameList[i]+'助力'+park_pin+'】：'+'已经助力过了！')
                    elif res['data']['helpState'] == 3:
                        print('【'+pinNameList[i]+'助力'+park_pin+'】：'+'没有助力次数了！')
                    elif res['data']['helpState'] == 4:
                        print('----------------------------------'+park_pin+'助力完成了！')
                        break
            except:
                continue
        get_reward(mycookie,park_pin)
    else:
        print('活动火爆了')

def use_thread(jd15_cookies, park_pins, cookiesList, pinNameList):
    threads = []
    for i in range(len(jd15_cookies)):
        threads.append(
            threading.Thread(target=help, args=(jd15_cookies[i], park_pins[i], cookiesList, pinNameList))
        )
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def start():
    printT("############{}##########".format(script_name))
    park_pins = getPinEnvs()
    get_jd_cookie = getJDCookie()
    cookiesList, pinNameList = get_jd_cookie.getcookies()
    jd15_cookies = []
    nicks = []
    for ckname in park_pins:
        try:
            ckNum = pinNameList.index(ckname)
            jd15_cookies.append(cookiesList[ckNum])
            # nicks.append(nickNameList[ckNum])
        except Exception as e:
            try:
                ckNum = pinNameList.index(unquote(ckname))
                jd15_cookies.append(cookiesList[ckNum])
                # nicks.append(nickNameList[ckNum])
            except:
                print(f"请检查被助力账号【{ckname}】名称是否正确？ck是否存在？提示：助力名字可填pt_pin的值、也可以填账号名。")
                continue
    if len(jd15_cookies) == 0:
        exit(4)
    use_thread(jd15_cookies, park_pins, cookiesList, pinNameList)


if __name__ == '__main__':
    start()
