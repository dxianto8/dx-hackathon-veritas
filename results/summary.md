# Results on Scams 2026 (held-out, never used for training or thresholds)

| system                                                                         | language   | scams_caught   |   recall |   missed_scams | false_alarms   |   precision |   f1 |
|:-------------------------------------------------------------------------------|:-----------|:---------------|---------:|---------------:|:---------------|------------:|-----:|
| Always 'not scam' (baseline)                                                   | ALL        | 0/60           |     0    |             60 | 0/60           |        0    | 0    |
| Always 'not scam' (baseline)                                                   | en         | 0/20           |     0    |             20 | 0/20           |        0    | 0    |
| Always 'not scam' (baseline)                                                   | es         | 0/20           |     0    |             20 | 0/20           |        0    | 0    |
| Always 'not scam' (baseline)                                                   | zh         | 0/20           |     0    |             20 | 0/20           |        0    | 0    |
| TF-IDF + LR, English-trained (baseline)                                        | ALL        | 13/60          |     0.22 |             47 | 8/60           |        0.62 | 0.32 |
| TF-IDF + LR, English-trained (baseline)                                        | en         | 11/20          |     0.55 |              9 | 6/20           |        0.65 | 0.59 |
| TF-IDF + LR, English-trained (baseline)                                        | es         | 1/20           |     0.05 |             19 | 0/20           |        1    | 0.1  |
| TF-IDF + LR, English-trained (baseline)                                        | zh         | 1/20           |     0.05 |             19 | 2/20           |        0.33 | 0.09 |
| Layer 1: multilingual embeddings + LR                                          | ALL        | 45/60          |     0.75 |             15 | 12/60          |        0.79 | 0.77 |
| Layer 1: multilingual embeddings + LR                                          | en         | 16/20          |     0.8  |              4 | 5/20           |        0.76 | 0.78 |
| Layer 1: multilingual embeddings + LR                                          | es         | 14/20          |     0.7  |              6 | 3/20           |        0.82 | 0.76 |
| Layer 1: multilingual embeddings + LR                                          | zh         | 15/20          |     0.75 |              5 | 4/20           |        0.79 | 0.77 |
| Upper bound: share of scams that reach agent (threshold routing)               | ALL        | 40/60          |     0.67 |             20 | 11/60          |        0.78 | 0.72 |
| Upper bound: share of scams that reach agent (threshold routing)               | en         | 13/20          |     0.65 |              7 | 4/20           |        0.76 | 0.7  |
| Upper bound: share of scams that reach agent (threshold routing)               | es         | 13/20          |     0.65 |              7 | 3/20           |        0.81 | 0.72 |
| Upper bound: share of scams that reach agent (threshold routing)               | zh         | 14/20          |     0.7  |              6 | 4/20           |        0.78 | 0.74 |
| Upper bound: share of scams that reach agent (threshold + tool-signal routing) | ALL        | 57/60          |     0.95 |              3 | 16/60          |        0.78 | 0.86 |
| Upper bound: share of scams that reach agent (threshold + tool-signal routing) | en         | 19/20          |     0.95 |              1 | 6/20           |        0.76 | 0.84 |
| Upper bound: share of scams that reach agent (threshold + tool-signal routing) | es         | 19/20          |     0.95 |              1 | 5/20           |        0.79 | 0.86 |
| Upper bound: share of scams that reach agent (threshold + tool-signal routing) | zh         | 19/20          |     0.95 |              1 | 5/20           |        0.79 | 0.86 |

## Mistakes made by: pred_layer1

| language   | label   | scam_type               | text                                                                                                                                           |   p_layer1 |
|:-----------|:--------|:------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------|-----------:|
| en         | scam    | bank_account_hold       | Wells Fargo: a hold has been placed on your account. Reactivate now to avoid closure: http://wellsfarg0-secure.com/verify                      | 0.30146    |
| en         | scam    | job_task                | Hello, Walmart HR is hiring online assessors. Work from home, $250/day, no experience needed. Reply YES if interested.                         | 0.320647   |
| en         | scam    | wrong_number            | Hi Mark, are we still on for coffee tomorrow at 10? It's Jessica from the yoga class.                                                          | 0.168722   |
| en         | scam    | wrong_number            | Sorry, wrong number! You seem kind though. I'm Lily, I work in crypto investing in Singapore. Would you like to be friends?                    | 0.457255   |
| en         | legit   | verification_code       | Your Google verification code is 482913. Don't share this code with anyone.                                                                    | 0.964197   |
| en         | legit   | verification_code       | Venmo: 731052 is your verification code. Never share this code. Venmo will never call to ask for it.                                           | 0.824045   |
| en         | legit   | bank_alert              | Chase: A $45.20 card purchase at TARGET was made on 11/14. If this wasn't you, call the number on the back of your card. No reply needed.      | 0.923281   |
| en         | legit   | everyday                | Can you send me the address for the party?                                                                                                     | 0.519568   |
| en         | legit   | toll_real               | Your E-ZPass statement is available. Log in to your account at e-zpassny.com to view it.                                                       | 0.678569   |
| es         | scam    | bank_account_hold       | Wells Fargo: su cuenta ha sido bloqueada temporalmente. Reactívela ahora para evitar el cierre: http://wellsfarg0-seguro.com/verificar         | 0.374925   |
| es         | scam    | job_task                | Hola, Walmart está contratando evaluadores en línea. Trabajo desde casa, $250 al día, sin experiencia. Responda SÍ si le interesa.             | 0.296529   |
| es         | scam    | job_task                | ¡Felicidades! Sus tareas de optimización generaron $1,480. Para retirar sus ganancias, deposite 200 USDT y complete la última serie de tareas. | 0.353301   |
| es         | scam    | wrong_number            | Hola Carlos, ¿seguimos con el café mañana a las 10? Soy Jessica, de la clase de yoga.                                                          | 0.0245937  |
| es         | scam    | wrong_number            | Perdón, número equivocado. Pareces muy amable. Soy Lily, trabajo en inversiones de criptomonedas en Singapur. ¿Te gustaría ser mi amigo?       | 0.314258   |
| es         | scam    | bank_account_hold       | BBVA: Su tarjeta ha sido desactivada por seguridad. Para reactivarla ingrese a bbva-mx-seguridad.icu                                           | 0.373838   |
| es         | legit   | verification_code       | Tu código de verificación de Google es 482913. No lo compartas con nadie.                                                                      | 0.940585   |
| es         | legit   | verification_code       | WhatsApp: tu código es 731-052. No compartas este código con nadie.                                                                            | 0.829529   |
| es         | legit   | bank_alert              | Chase: Se realizó una compra de $45.20 en TARGET el 14/11. Si no fue usted, llame al número al reverso de su tarjeta.                          | 0.787583   |
| zh         | scam    | authority_impersonation | 【中国驻芝加哥总领事馆】您有一份重要文件待领取，涉及您的护照问题。逾期将影响您的签证，请立即回电 1-312-555-0166 按9转人工。                                                                         | 0.125717   |
| zh         | scam    | authority_impersonation | 您好，这里是上海市公安局。您的身份证涉嫌一起洗钱案件，请立即添加办案警官微信配合调查，否则将发布通缉令。                                                                                           | 0.466874   |
| zh         | scam    | insurance_impersonation | 【医保理赔部】系统显示您近期在中国有一笔手术理赔申请，金额$8,600。如非本人申请，请回复1联系专员核实。                                                                                         | 0.40444    |
| zh         | scam    | wrong_number            | 王姐，明天上午10点的茶还约吗？我是瑜伽课的小琳。                                                                                                                      | 0.00564839 |
| zh         | scam    | wrong_number            | 不好意思发错了。不过你看起来人很好，我叫Lily，在新加坡做加密货币投资，可以交个朋友吗？                                                                                                  | 0.27393    |
| zh         | legit   | verification_code       | 【微信】验证码：482913，用于登录验证，请勿泄露给他人。                                                                                                                 | 0.921731   |
| zh         | legit   | verification_code       | Your Google verification code is 731052. 请勿将验证码告诉任何人。                                                                                          | 0.906515   |
| zh         | legit   | bank_alert              | 【Chase】您的信用卡于11/14在TARGET消费$45.20。如非本人消费，请拨打卡背面的电话。                                                                                            | 0.958741   |
| zh         | legit   | delivery                | 【UPS】您的包裹预计今天下午2点至6点送达。查询：https://www.ups.com/track?tracknum=1Z999AA10123456784                                                                | 0.812929   |
