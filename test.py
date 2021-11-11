#!/bin/env python3
# -*- coding: utf-8 -*

import time, datetime, os, sys, random
import requests, re, json
from urllib.parse import quote, unquote
import threading

cookies = ''


def printT(s):
    print("[{}]: {}".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), s))
    sys.stdout.flush()


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
    def getCookie(self):
        global cookies
        ckfile = self.getckfile()
        try:
            if os.path.exists(ckfile):
                with open(ckfile, "r", encoding="utf-8") as f:
                    cks_text = f.read()
                    f.close()
                if 'pt_key=' in cks_text and 'pt_pin=' in cks_text:
                    r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
                    cks_list = r.findall(cks_text)
                    if len(cks_list) > 0:
                        cookies = ''
                        for i in cks_list:
                                cookies += i
                        return

            if "JD_COOKIE" in os.environ:
                if len(os.environ["JD_COOKIE"]) > 10:
                    cookies = os.environ["JD_COOKIE"]
                    printT("已获取并使用Env环境 Cookie")
        except Exception as e:
            printT(f"【getCookie Error】{e}")

        # 检测cookie格式是否正确

    def getUserInfo(self, ck, pinName, userNum):
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
            if sys.platform == 'ios':
                resp = requests.get(url=url, verify=False, headers=headers, timeout=60).json()
            else:
                resp = requests.get(url=url, headers=headers, timeout=60).json()
            if resp['retcode'] == "0":
                nickname = resp['data']['userInfo']['baseInfo']['nickname']
                return ck, nickname
            else:
                context = f"账号{userNum}【{pinName}】Cookie 已失效！请重新获取。"
                print(context)
                return ck, False
        except Exception:
            context = f"账号{userNum}【{pinName}】Cookie 已失效！请重新获取。"
            print(context)
            return ck, False

    def iscookie(self):
        """
        :return: cookiesList,userNameList,pinNameList
        """
        cookiesList = []
        userNameList = []
        pinNameList = []
        if 'pt_key=' in cookies and 'pt_pin=' in cookies:
            r = re.compile(r"pt_key=.*?pt_pin=.*?;", re.M | re.S | re.I)
            result = r.findall(cookies)
            if len(result) >= 1:
                printT("您已配置{}个账号".format(len(result)))
                u = 1
                for i in result:
                    r = re.compile(r"pt_pin=(.*?);")
                    pinName = r.findall(i)
                    pinName = unquote(pinName[0])
                    # 获取账号名
                    ck, nickname = self.getUserInfo(i, pinName, u)
                    if nickname != False:
                        cookiesList.append(ck)
                        userNameList.append(nickname)
                        pinNameList.append(pinName)
                    else:
                        u += 1
                        continue
                    u += 1
                if len(cookiesList) > 0 and len(userNameList) > 0:
                    return cookiesList, userNameList, pinNameList
                else:
                    printT("没有可用Cookie，已退出")
                    exit(3)
            else:
                printT("cookie 格式错误！...本次操作已退出")
                exit(4)
        else:
            printT("cookie 格式错误！...本次操作已退出")
            exit(4)


if __name__ == '__main__':
    printT(os.environ)
    # get_jd_cookie = getJDCookie()
    # get_jd_cookie.getckfile()
