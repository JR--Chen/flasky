import re
import pytesseract
from PIL import Image
from io import BytesIO
from datetime import datetime
try:
    from .baseSpider import BaseSpider

except :
    from baseSpider import BaseSpider

index_url = 'http://202.97.210.38:9002/usr_cardb_main.ktcl'
login_url = 'http://202.97.210.38:9002/usr_cardb_proc.ktcl'
balance_url = 'http://202.97.210.38:9002/cardb_acct_bal.ktcl'
detail_url = 'http://202.97.210.38:9002/cardb_acct_det.ktcl'
host = 'http://202.97.210.38:9002/'

detail_pattern = "\n<td align=center rowspan=1>(.*?)</td>\n" \
         "<td align=center nowrap rowspan=1>(.*?)</td>\n" \
         "<td align=center nowrap rowspan=1>(.*?)</td>\n" \
         "<td align=center rowspan=1 nowrap>.*?</td>\n" \
         "<td align=right rowspan=1 nowrap>.*?</td>\n" \
         "<td align=right rowspan=1 nowrap>0/0</td>\n" \
         "<td align=right rowspan=1 nowrap>0/0</td>\n" \
         "<td align=right rowspan=1 nowrap>0</td>\n" \
         "<td align=right rowspan=1 nowrap>0</td>\n" \
         "<td align=center rowspan=1 nowrap>.*?</td>\n" \
         "<td align=center rowspan=1>&nbsp;</td>\n" \
         "<td align=center rowspan=1>&nbsp;</td>\n" \
         "<td align=center rowspan=1 nowrap>0</td>\n" \
         "<td align=center rowspan=1 nowrap>.*?</td>\n" \
         "<td align=right nowrap=1 rowspan=1>(.*?)</td>\n" \
         "<td rowspan=1 align=right nowrap=1>.*?</td>\n<" \
         "td rowspan=1 align=right nowrap=1>.*?</td>\n" \
         "<td rowspan=1 align=right nowrap=1>0.00</td>\n" \
         "<td nowrap=1 align=center>.*?</td>\n" \
         "<td align=right nowrap=1>.*?</td>\n" \
         "<td align=right nowrap=1>.*?</td>\n" \
         "<td align=right nowrap=1>0</td>\n" \
         "<td align=right nowrap=1>.*?</td>\n"


class AiobsSpider(BaseSpider):
    def __init__(self, card_id, password):
        super().__init__()
        self.card_id = card_id
        self.password = password
        self.key = None
        self.code = None
        self.balance = None
        self.begin_date = None
        self.balance_select_value = None
        self.detail_select_value = None

    def login(self):
        data = {
            'card_id': self.card_id,
            'password': self.password,
            'key': self.key,
            'code': self.code
        }
        resp = super().get_html(login_url, 'POST', data=data)
        content = resp.text.encode('ISO-8859-1').decode('gbk')
        balance = re.search("<td align=center><input type='radio' CHECKED name='select' value=(.*?)></td><td align=center nowrap>.*?</td><td align=center nowrap>.*?</td><td align=center nowrap>"
                         ".*?</td><td align=center nowrap>人民币</td><td align=center nowrap>(.*?)</td><td align=center nowrap>.*?</td><td align=center nowrap>人工加锁</td>", content)
        if balance is not None:
            self.balance_select_value = balance.group(1)
            self.begin_date = balance.group(2)

            detail = re.search("<td align=center><input type='radio' CHECKED name='select' value=(.*?)></td><td align=center nowrap>.*?</td><td align=center nowrap>.*?</td><td align=center nowrap>宽带PPPOE\(Cable-PPPoE服务模板\)"
                               "</td><td align=center nowrap>.*?</td><td align=center nowrap>人工加锁</td></tr>", content)
            self.detail_select_value = detail.group(1)
            return 200
        else:
            return 400

    def get_key_and_code(self):
        resp = super().get_html(index_url, 'GET')

        content = resp.text
        item = re.search("""<input type="text" name="code" value="" size="4" maxlength="4">
         .*?<img src=(.*?) >.*?<input type=hidden name='key' value='(.*?)'>""", content, re.S)

        codeURL = item.group(1)[2:]
        self.code = self.get_code(codeURL)
        self.key = item.group(2)

    def get_code(self, codeURL):
        codeURL = host+codeURL
        resp = super().get_html(codeURL, 'GET')
        image = Image.open(BytesIO(resp.content))
        code = pytesseract.image_to_string(image)

        return code

    def get_balance(self):
        data = {
            'select': self.balance_select_value
        }
        resp = super().get_html(balance_url, 'POST', data=data)
        content = resp.text.encode('ISO-8859-1').decode('gbk')

        item = re.search('<td>现金</td>.*?<td>(.*?)</td>.*?<td>元</td>', content, re.S)

        balance = item.group(1)
        self.balance = balance

        return balance

    def get_use_detial(self):
        item = re.search('(.*?)年(.*?)月(.*?)日', self.begin_date)
        s_year, s_month, s_day = item.group(1), item.group(2), item.group(3)
        data = {
            'e_day': datetime.now().day,
            'e_month': datetime.now().month,
            'e_year': datetime.now().year,
            's_day': s_day,
            's_month': s_month,
            's_year': s_year,
            'select': self.detail_select_value
        }

        resp = super().get_html(detail_url, 'POST', data=data)
        content = resp.text.encode('ISO-8859-1').decode('gbk')
        details = re.findall(detail_pattern, content, re.S)
        next_page = re.search("<a href='(.*?)' >", content, re.S)

        if next_page is not None:
            result = self._get_detail_next_page(next_page)
            if result != []:
                for x in result:
                    details.append(x)

        return details

    def _get_detail_next_page(self, next_page):
        next_page_url = host + next_page.group(1)
        resp = super().get_html(next_page_url, 'GET')
        content = resp.text.encode('ISO-8859-1').decode('gbk')
        details = re.findall(detail_pattern, content, re.S)

        return details


if __name__ == '__main__':
    user = AiobsSpider(4510002871086, '45p7tjxo')
    user.get_key_and_code()
    status = user.login()
    result = user.get_use_detial()

    # print(result)

