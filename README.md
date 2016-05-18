# PayApp

(비공식) 모바일 결제 서비스 PayApp(http://www.payapp.kr)의 파이썬 바인딩.

파이썬 3.4/3.5에서 테스트했으며 2.7 호환 코드를 작성하긴 했으나 하위 버전에서의 정상 작동을 보장하지는 않습니다.

---

## 설치

pip를 이용해 설치하거나 레포를 복제한 후에 사용하는 방법이 있습니다.

```bash
$ pip install payapp
```

### 의존성

이 패키지는 다음 패키지들을 필요로 합니다.

 - requests
 
## 사용 방법
 
### Flask

```python
from flask import Flask
from flask import requests, url_for
from payapp import PayApp

app = Flask(__name__)
pay = PayApp(PayApp.TEST_ID, PayApp.TEST_KEY, PayApp.TEST_VALUE)

@app.route('/')
def index():
    callback_url = url_for('.callback', _external=True)
    result = pay.pay_result(
        name=u'bery tasti fud',
        price='1000',
        contact='01000000000',
        returns='', # => 모바일에서 결제가 완료된 후 보여줄 페이지 URL
        callback=callback_url # => 백노티가 전달되는 URL
    )
    result.success # => 성공여부
    result.error # => 실패일 때 에러메시지
    result.identifier # => 결제 ID (payapp api의 mul_no)

    return result.url # => 결제 URL (모바일로 전송됨)

# callback url(payapp api의 feedback url)의 경우 특정 이벤트가 있을 때
# 백그라운드로 전달됩니다.
# 이 부분에서 state를 확인한 후 DB에 미리 state를 기록한 후에
# 프론트엔드에서 ajax 폴링/롱폴링 또는 '결제완료' 버튼을 통해
# 확인하도록 구현하면 됩니다.
@app.route('/callback', methods=['POST'])
def callback():
    data = request.form.to_dict()
    if not pay.verify_callback(data):  # 올바른 콜백 데이터인지 검증
        return 'FAIL'
        
    parsed = pay.parse_callback(data)  # 원하는 데이터로 가공
    parsed.identifier # => 결제 ID (payapp api의 mul_no)
    parsed.req_date # => python datetime 형식의 요청 날짜 및 시간
    parsed.pay_date # => python datetime 형식의 결제 날짜 및 시간 (결제 state일 때만 유효)
    parsed.pay_type # => payapp 문서 참고
    parsed.pay_state # => payapp 문서 참고
    
    # 신용카드 거래일 때 유효한 속성
    pay.pay_check_url # => 카드전표 URL
    pay.pay_card_name # => 결제 카드사 이름
    
    # 가상계좌 거래일 때 유효한 속성
    pay.pay_vbank # => 가상계좌 은행 이름
    pay.pay_vbank_account # => 가상계좌 계좌번호

    return 'SUCCESS'
    
@app.route('/cancel', methods=['GET'])
def cancel():
    identifier = request.args.get('id')
    memo = request.args.get('memo', '취소') # => 취소 사유 (문자로 전달됩니다)
    result = pay.pay_cancel(identifier=identifier, memo=memo)

    return result.success
    
if __name__ == '__main__':
    app.run(debug=True, threaded=True)
```

## 라이센스

Python용 PayApp 바인딩인 ssut/payapp 프로젝트는 MIT 허가서(MIT License)를 따릅니다:

```
The MIT License (MIT)

Copyright (c) 2016 SuHun Han

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```