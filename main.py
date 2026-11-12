import sys
import requests as r
import json
import telepot

tele_enable = False
sc_enable = False
qq_enable = False
pp_enable = False
sign_url = 'https://n.cg.163.com/api/v2/sign-today'
current = 'https://n.cg.163.com/api/v2/client-settings/@current'


cookies = sys.argv[1].split('#')
teleid = sys.argv[2]
teletoken = sys.argv[3]
sckey = sys.argv[4]
qqkey = sys.argv[5]
ppkey = sys.argv[6]

if cookies == "" or cookies == []:
    print('[网易云游戏自动签到]未设置cookie，正在退出……')
    sys.exit()
if teleid != "" and teletoken != "":
    tele_enable = True
    print('Telegram推送已配置！')
    bot = telepot.Bot(teletoken)
else:
    print('未配置Telegram推送！')
if sckey != "":
    sc_enable = True
    print('ServerChan推送已配置！')
else:
    print('未配置ServerChan推送！')
if qqkey != "":
    qq_enable = True
    print('QQ推送已配置！')
else:
    print('未配置QQ推送！')
if ppkey != '':
    pp_enable = True
    print('PushPlus推送已配置！')
else:
    print('未配置PushPlus推送！')

class ScriptRunError(Exception):
    print("[网易云游戏自动签到]脚本运行错误，具体请参见日志！")


def signin(url, cookie):
    header = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5',
        'Authorization': str(cookie),
        'Connection': 'keep-alive',
        'Content-Length': '0',
        'Host': 'n.cg.163.com',
        'Origin': 'https://cg.163.com',
        'Referer': 'https://cg.163.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'X-Platform': '0'
    }

    result = r.post(url=url, headers=header)
    return result


def getme(url, cookie):
    header = {
        'Host': 'n.cg.163.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
        'X-Platform': '0',
        'Authorization': str(cookie),
        'Origin': 'https://cg.163.com',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://cg.163.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5'
    }
    result = r.get(url=url, headers=header)
    return result


def send(id, message):
    if tele_enable:
        print('正在使用Telebot进行消息推送……')
        bot.sendMessage(id, message, parse_mode=None, disable_web_page_preview=None, disable_notification=None,
                        reply_to_message_id=None, reply_markup=None)
        print('Telebot消息推送完成！')


def scsend(SCKEY, message):
    sc_url = 'http://sctapi.ftqq.com/{}.send?title=网易云游戏自动签到脚本&desp={}'.format(SCKEY, message)
    if sc_enable:
        print('正在使用ServerChan进行消息推送……')
        r.get(url=sc_url)
        print('ServerChan消息推送完成！')
        
def qqsend(QQKEY, message):
    qq_url = 'https://push.xuthus.cc/send/{}?c=网易云游戏自动签到脚本\n{}'.format(QQKEY, message)
    if qq_enable:
        print('正在进行QQ消息推送……')
        r.get(url=qq_url)
        print('QQ消息推送完成！')

def ppsend(PPKEY, message):
    pp_url = 'http://pushplus.hxtrip.com/send?token={}&title=网易云游戏自动签到脚本&content={}&template=html'.format(PPKEY, message)
    if pp_enable:
        print('正在使用PushPlus进行消息推送……')
        r.get(url=pp_url)
        print('PushPlus消息推送完成')

if __name__ == "__main__":
    print('检测到{}个账号，即将开始签到！'.format(len(cookies)))
    success = []
    failure = []
    msg = []
    for index, cookie in enumerate(cookies, start=1):
        label = '第{}个账号'.format(index)
        if not cookie.strip():
            msg.append('{}：Cookie 为空，请检查 Secrets.COOKIE'.format(label))
            failure.append(cookie)
            continue

        # 验证登录态
        try:
            me = getme(current, cookie)
        except Exception as e:
            msg.append('{}验证请求异常（网络错误）：{}'.format(label, e))
            failure.append(cookie)
            continue

        if me.status_code in (401, 403):
            msg.append('{}验证失败：Cookie 已过期或无效（HTTP {}）。'
                       '请重新抓取 Authorization 并更新仓库 Secrets.COOKIE'.format(label, me.status_code))
            failure.append(cookie)
            continue
        if me.status_code != 200:
            msg.append('{}验证失败：接口返回 HTTP {}，响应：{}'.format(
                label, me.status_code, me.text[:200]))
            failure.append(cookie)
            continue

        # 执行签到
        try:
            sign_return = signin(sign_url, cookie)
        except Exception as e:
            msg.append('{}签到请求异常（网络错误）：{}'.format(label, e))
            failure.append(cookie)
            continue

        if sign_return.status_code == 200:
            msg.append('{}签到成功！'.format(label))
            success.append(cookie)
        else:
            msg.append('{}签到失败：HTTP {}，响应：{}'.format(
                label, sign_return.status_code, sign_return.text[:200]))
            failure.append(cookie)
    outputmsg = str(msg).replace("[", '').replace(']', '').replace(',', '<br>').replace('\'', '')
    teleinfomsg = '''
    感谢使用来自GamerNoTitle的网易云游戏自动签到脚本！
    今日签到结果如下：
    成功数量：{0}/{2}
    失败数量：{1}/{2}
    具体情况如下：
    {3}
    GamerNoTitle: https://bili33.top
    网易云游戏自动签到脚本: https://github.com/GamerNoTitle/wyycg-autocheckin
    '''.format(len(success), len(failure), len(cookies), outputmsg)
    scinfomsg = '''
    感谢使用来自<a herf='https://bili33.top'>GamerNoTitle</a>的<a herf='https://github.com/GamerNoTitle/wyycg-autocheckin'>网易云游戏自动签到脚本</a>！<br>
    今日签到结果如下：<br>
    成功数量：{0}/{2}<br>
    失败数量：{1}/{2}<br>
    具体情况如下：<br>
    {3}
    GamerNoTitle: https://bili33.top
    网易云游戏自动签到脚本: https://github.com/GamerNoTitle/wyycg-autocheckin
    '''.format(len(success), len(failure), len(cookies), outputmsg)
    qqinfomsg = '''
    感谢使用来自bili33.top GamerNoTitle的网易云游戏自动签到脚本
    今日签到结果如下：
    成功数量：{0}/{2}
    失败数量：{1}/{2}
    具体情况如下：
    {3}
    GamerNoTitle: https://bili33.top
    网易云游戏自动签到脚本: https://github.com/GamerNoTitle/wyycg-autocheckin
    '''.format(len(success), len(failure), len(cookies), outputmsg)
    ppinfomsg = '''
    感谢使用来自bili33.top GamerNoTitle的网易云游戏自动签到脚本
    今日签到结果如下：
    成功数量：{0}/{2}
    失败数量：{1}/{2}
    具体情况如下：
    {3}
    GamerNoTitle: https://bili33.top
    网易云游戏自动签到脚本: https://github.com/GamerNoTitle/wyycg-autocheckin
    '''.format(len(success), len(failure), len(cookies), outputmsg)

    send(teleid, teleinfomsg)
    scsend(sckey, scinfomsg)
    qqsend(qqkey, qqinfomsg)
    ppsend(ppkey, ppinfomsg)
    print(teleinfomsg)

    # 把结果写到 GitHub Actions 的 Step Summary，失败原因在 run 页面顶部即可见
    try:
        import os
        summary_path = os.environ.get('GITHUB_STEP_SUMMARY')
        if summary_path:
            lines = ['## 网易云游戏签到结果', '',
                     '- 成功：**{}** / {}'.format(len(success), len(cookies)),
                     '- 失败：**{}** / {}'.format(len(failure), len(cookies)), '']
            lines += ['- {}'.format(m) for m in msg]
            if failure:
                lines += ['', '> 需要处理：登录态已失效。请从 cg.163.com 重新获取 '
                          '`Authorization` 请求头，并更新仓库 Secrets 中的 `COOKIE`。']
            with open(summary_path, 'a', encoding='utf-8') as f:
                f.write('\n'.join(lines) + '\n')
    except Exception as e:
        print('写入 Step Summary 失败（不影响签到）：{}'.format(e))

    if failure:
        raise ScriptRunError('{} / {} 个账号签到失败，详情见上方日志与 Step Summary'.format(
            len(failure), len(cookies)))
