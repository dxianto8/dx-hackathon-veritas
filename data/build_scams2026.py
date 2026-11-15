"""Builds data/scams2026.csv — the 'Scams 2026' multilingual test set.

Every SCAM row is modelled on a scam type described in a public government
warning (source_url). LEGIT rows are ordinary everyday texts, including
hard cases (real-looking bank alerts, real verification codes, real carrier
domains) so we can measure false alarms.

origin=ai_written: drafted with an AI assistant from the cited warning. The team
should review every row, and replace rows with real quoted examples where a
public source quotes one.
"""
import csv
from pathlib import Path

FTC_TOLL = "https://consumer.ftc.gov/consumer-alerts/2025/01/got-text-about-unpaid-tolls-its-probably-scam"
FCC_TOLL = "https://www.fcc.gov/consumer-governmental-affairs/how-spot-and-avoid-toll-road-payment-scam-texts"
FTC_TOP = "https://www.ftc.gov/news-events/data-visualizations/data-spotlight/2025/04/top-text-scams-2024"
FCC_PKG = "https://www.fcc.gov/how-identify-and-avoid-package-delivery-scams"
FTC_TASK = "https://consumer.ftc.gov/consumer-alerts/2025/08/how-spot-avoid-task-scams"
FTC_JOB26 = "https://consumer.ftc.gov/consumer-alerts/2026/04/job-offer-text-probably-scam"
FTC_JOB26_ES = "https://consumidor.ftc.gov/alertas-para-consumidores/2026/04/es-probable-que-ese-mensaje-de-texto-con-una-propuesta-de-trabajo-sea-una-estafa"
FCC_GLOSS = "https://www.fcc.gov/scam-glossary"
FBI_CN_POLICE = "https://www.fbi.gov/investigate/cyber/alerts/2024/chinese-police-imposters-incorporate-aggressive-tactics-to-target-us-based-chinese-community"
FBI_CN_INS = "https://www.fbi.gov/investigate/cyber/alerts/2025/criminals-impersonate-us-health-insurance-providers-and-chinese-law-enforcement-to-target-chinese-speakers-residing-in-the-united-states"
FCC_CN = "https://www.fcc.gov/chinese-language-robocall-scams"
FTC_CONSULATE = "https://consumer.ftc.gov/consumer-alerts/2018/04/scammers-impersonate-chinese-consulate"
SELF = "self-written everyday message"

S, L = "scam", "legit"

ROWS = [
# ---------------- English scams ----------------
("en", S, "toll_fee", FTC_TOLL, "E-ZPass: You have an unpaid toll balance of $4.35. To avoid a $50 late fee and suspension of your account, pay now: https://ezpass-tollpay.top/pay"),
("en", S, "toll_fee", FCC_TOLL, "IL Tollway notice: our records show an outstanding toll of $6.80. Pay within 24 hours to avoid penalties. getipass-il.xyz/settle"),
("en", S, "toll_fee", FTC_TOLL, "SunPass: Final reminder. Your unpaid toll of $3.95 will be sent to collections today. Reply Y then open the link to pay: sunpass-billing.icu"),
("en", S, "package_fee", FTC_TOP, "USPS: Your package is on hold due to an incomplete address. Update within 12 hours or it will be returned: https://usps-redelivery.top/us"),
("en", S, "package_fee", FCC_PKG, "Hi, we are having issues releasing your package. Please update shipping directions ups-track.click/1ebf9d Reply Stop to Opt Out"),
("en", S, "package_fee", FCC_PKG, "Your order is stuck in customs. A tariff of $2.99 must be paid before delivery: https://bit.ly/3tariffpay"),
("en", S, "package_fee", FTC_TOP, "FedEx: A $1.50 redelivery fee is required for parcel #US8823. Pay here: fedx-delivery.com/fee"),
("en", S, "fake_fraud_alert", FTC_TOP, "Amazon Fraud Dept: Did you authorize a purchase of iPhone 17 Pro for $1,249.00? Reply YES or NO. If not you, call 1-888-555-0143 immediately."),
("en", S, "fake_fraud_alert", FTC_TOP, "Chase Alert: Suspicious activity detected on your account. Your funds are at risk. Call our fraud team now at 1-844-555-0199 to move funds to a safe account."),
("en", S, "bank_account_hold", FCC_GLOSS, "Wells Fargo: a hold has been placed on your account. Reactivate now to avoid closure: http://wellsfarg0-secure.com/verify"),
("en", S, "bank_account_hold", FCC_GLOSS, "Bank of America: your online access is locked after unusual sign-in. Verify identity: http://45.137.21.9/boa/login"),
("en", S, "job_task", FTC_TASK, "Hi! I'm Emma from a recruitment agency. We have a remote part-time job rating apps online, earn $300-$800/day. Interested? Reply on WhatsApp +44 7700 900123"),
("en", S, "job_task", FTC_JOB26, "Hello, Walmart HR is hiring online assessors. Work from home, $250/day, no experience needed. Reply YES if interested."),
("en", S, "job_task", FTC_TASK, "Congrats! Your optimization tasks earned $1,480. To unlock withdrawal, deposit 200 USDT to complete your final task set."),
("en", S, "wrong_number", FTC_TOP, "Hi Mark, are we still on for coffee tomorrow at 10? It's Jessica from the yoga class."),
("en", S, "wrong_number", FTC_TOP, "Sorry, wrong number! You seem kind though. I'm Lily, I work in crypto investing in Singapore. Would you like to be friends?"),
("en", S, "fake_fraud_alert", FTC_TOP, "PayPal: We noticed a login from a new device in Lagos, NG. If this wasn't you, secure your account: paypa1-support.com/secure"),
("en", S, "package_fee", FTC_TOP, "USPS: The package arrived at the warehouse but cannot be delivered. Reschedule: https://xn--usp-1na.com/track"),
("en", S, "toll_fee", FCC_TOLL, "Dear Customer, FasTrak: You owe $12.51 in toll charges. Pay now or your license will be suspended. fastrak-payment.vip"),
("en", S, "job_task", FTC_JOB26, "Amazon Recruiting: remote position available, $120/hour, flexible schedule. Reply INTERESTED to receive details."),
# ---------------- English legit ----------------
("en", L, "everyday", SELF, "Hey, I'm running 10 minutes late, save me a seat!"),
("en", L, "everyday", SELF, "Mom, can you pick me up from practice at 6:30?"),
("en", L, "everyday", SELF, "Dinner at grandma's on Sunday, bring the pie please"),
("en", L, "verification_code", SELF, "Your Google verification code is 482913. Don't share this code with anyone."),
("en", L, "verification_code", SELF, "Venmo: 731052 is your verification code. Never share this code. Venmo will never call to ask for it."),
("en", L, "appointment", SELF, "Reminder: your dental cleaning is Tue Nov 18 at 3:15 PM with Dr. Patel. Reply C to confirm or call the office to reschedule."),
("en", L, "bank_alert", SELF, "Chase: A $45.20 card purchase at TARGET was made on 11/14. If this wasn't you, call the number on the back of your card. No reply needed."),
("en", L, "delivery", SELF, "Amazon: Your package was delivered. Track at amazon.com/orders"),
("en", L, "delivery", SELF, "UPS: Your package will arrive today between 2pm and 6pm. Track: https://www.ups.com/track?tracknum=1Z999AA10123456784"),
("en", L, "school", SELF, "Lincoln High: Early dismissal tomorrow at 12:30 PM due to staff training."),
("en", L, "everyday", SELF, "Did you finish the chem lab write-up? I'm stuck on question 4"),
("en", L, "pharmacy", SELF, "CVS Pharmacy: Your prescription is ready for pickup at 123 Main St. Reply STOP to opt out."),
("en", L, "everyday", SELF, "Happy birthday!! Hope you have the best day"),
("en", L, "everyday", SELF, "Can you send me the address for the party?"),
("en", L, "bank_alert", SELF, "Bank of America: Your direct deposit of $1,250.00 has posted to your checking account."),
("en", L, "work", SELF, "Hi, this is Sarah from the library. Your shift on Saturday is moved to 11am-3pm. Thanks!"),
("en", L, "everyday", SELF, "Grandpa says the heater is broken again, can you call him?"),
("en", L, "toll_real", SELF, "Your E-ZPass statement is available. Log in to your account at e-zpassny.com to view it."),
("en", L, "everyday", SELF, "Ok sounds good, see you at 7"),
("en", L, "everyday", SELF, "Don't forget the soccer game moved to Field 3"),
# ---------------- Spanish scams ----------------
("es", S, "toll_fee", FTC_TOLL, "E-ZPass: Tiene un peaje pendiente de $4.35. Para evitar un cargo de $50 y la suspensión de su cuenta, pague ahora: https://ezpass-pagos.top/pagar"),
("es", S, "toll_fee", FCC_TOLL, "Aviso de peaje: nuestros registros muestran un saldo pendiente de $6.80. Pague en 24 horas para evitar multas: getipass-il.xyz/pago"),
("es", S, "package_fee", FTC_TOP, "USPS: Su paquete está retenido por una dirección incompleta. Actualice sus datos en 12 horas o será devuelto: https://usps-entrega.top/es"),
("es", S, "package_fee", FCC_PKG, "Su pedido está retenido en aduana. Debe pagar un arancel de $2.99 antes de la entrega: https://bit.ly/aduana-pago"),
("es", S, "package_fee", FTC_TOP, "FedEx: Se requiere una tarifa de reenvío de $1.50 para su paquete #US8823. Pague aquí: fedx-entregas.com/tarifa"),
("es", S, "fake_fraud_alert", FTC_TOP, "Alerta de Amazon: ¿Autorizó una compra de $1,249.00? Responda SÍ o NO. Si no fue usted, llame de inmediato al 1-888-555-0143."),
("es", S, "fake_fraud_alert", FTC_TOP, "Chase: Detectamos actividad sospechosa en su cuenta. Su dinero está en riesgo. Llame al 1-844-555-0199 para transferir sus fondos a una cuenta segura."),
("es", S, "bank_account_hold", FCC_GLOSS, "Wells Fargo: su cuenta ha sido bloqueada temporalmente. Reactívela ahora para evitar el cierre: http://wellsfarg0-seguro.com/verificar"),
("es", S, "bank_account_hold", FCC_GLOSS, "Banco: su acceso en línea fue suspendido por un inicio de sesión inusual. Verifique su identidad: http://45.137.21.9/banco/login"),
("es", S, "job_task", FTC_JOB26_ES, "Hola, Walmart está contratando evaluadores en línea. Trabajo desde casa, $250 al día, sin experiencia. Responda SÍ si le interesa."),
("es", S, "job_task", FTC_TASK, "¡Hola! Soy Ana de una agencia de reclutamiento. Tenemos un trabajo remoto calificando aplicaciones, gane $300-$800 al día. Escríbame por WhatsApp +44 7700 900123"),
("es", S, "job_task", FTC_TASK, "¡Felicidades! Sus tareas de optimización generaron $1,480. Para retirar sus ganancias, deposite 200 USDT y complete la última serie de tareas."),
("es", S, "job_task", FTC_JOB26_ES, "Reclutamiento Amazon: puesto remoto disponible, $120 por hora, horario flexible. Responda ME INTERESA para recibir detalles."),
("es", S, "wrong_number", FTC_TOP, "Hola Carlos, ¿seguimos con el café mañana a las 10? Soy Jessica, de la clase de yoga."),
("es", S, "wrong_number", FTC_TOP, "Perdón, número equivocado. Pareces muy amable. Soy Lily, trabajo en inversiones de criptomonedas en Singapur. ¿Te gustaría ser mi amigo?"),
("es", S, "fake_fraud_alert", FTC_TOP, "PayPal: Detectamos un inicio de sesión desde un nuevo dispositivo. Si no fue usted, proteja su cuenta: paypa1-soporte.com/seguro"),
("es", S, "toll_fee", FCC_TOLL, "Estimado cliente, FasTrak: debe $12.51 en peajes. Pague ahora o su licencia será suspendida. fastrak-pago.vip"),
("es", S, "package_fee", FTC_TOP, "Correos USPS: el paquete llegó al almacén pero no se pudo entregar. Reprograme aquí: https://xn--usp-1na.com/rastreo"),
("es", S, "bank_account_hold", FCC_GLOSS, "BBVA: Su tarjeta ha sido desactivada por seguridad. Para reactivarla ingrese a bbva-mx-seguridad.icu"),
("es", S, "fake_fraud_alert", FTC_TOP, "Zelle: Se envió un pago de $950 desde su cuenta. Si no reconoce esta operación llame al 1-833-555-0177 para cancelarla."),
# ---------------- Spanish legit ----------------
("es", L, "everyday", SELF, "Voy 10 minutos tarde, guárdame un lugar"),
("es", L, "everyday", SELF, "Mamá, ¿me puedes recoger del entrenamiento a las 6:30?"),
("es", L, "everyday", SELF, "Cena en casa de la abuela el domingo, trae el pastel por favor"),
("es", L, "verification_code", SELF, "Tu código de verificación de Google es 482913. No lo compartas con nadie."),
("es", L, "verification_code", SELF, "WhatsApp: tu código es 731-052. No compartas este código con nadie."),
("es", L, "appointment", SELF, "Recordatorio: su cita con el Dr. Pérez es el martes 18 de noviembre a las 3:15 PM. Responda C para confirmar."),
("es", L, "bank_alert", SELF, "Chase: Se realizó una compra de $45.20 en TARGET el 14/11. Si no fue usted, llame al número al reverso de su tarjeta."),
("es", L, "delivery", SELF, "Amazon: Su paquete fue entregado. Consulte sus pedidos en amazon.com/orders"),
("es", L, "school", SELF, "Escuela Lincoln: Mañana salida temprano a las 12:30 PM por capacitación del personal."),
("es", L, "everyday", SELF, "¿Terminaste la tarea de química? No entiendo la pregunta 4"),
("es", L, "pharmacy", SELF, "Farmacia CVS: Su receta está lista para recoger en 123 Main St. Responda STOP para cancelar."),
("es", L, "everyday", SELF, "¡Feliz cumpleaños! Que pases un día increíble"),
("es", L, "everyday", SELF, "¿Me mandas la dirección de la fiesta?"),
("es", L, "bank_alert", SELF, "Bank of America: Su depósito directo de $1,250.00 ya está disponible en su cuenta de cheques."),
("es", L, "work", SELF, "Hola, soy Sara de la biblioteca. Tu turno del sábado cambió a 11am-3pm. ¡Gracias!"),
("es", L, "everyday", SELF, "El abuelo dice que la calefacción se descompuso otra vez, ¿le puedes llamar?"),
("es", L, "delivery", SELF, "UPS: Su paquete llegará hoy entre 2pm y 6pm. Rastreo: https://www.ups.com/track?tracknum=1Z999AA10123456784"),
("es", L, "everyday", SELF, "Ok, nos vemos a las 7"),
("es", L, "everyday", SELF, "No olvides que el partido de fútbol se cambió a la cancha 3"),
("es", L, "everyday", SELF, "Ya llegué a casa, gracias por traerme"),
# ---------------- Chinese scams ----------------
("zh", S, "authority_impersonation", FTC_CONSULATE, "【中国驻芝加哥总领事馆】您有一份重要文件待领取，涉及您的护照问题。逾期将影响您的签证，请立即回电 1-312-555-0166 按9转人工。"),
("zh", S, "authority_impersonation", FBI_CN_POLICE, "您好，这里是上海市公安局。您的身份证涉嫌一起洗钱案件，请立即添加办案警官微信配合调查，否则将发布通缉令。"),
("zh", S, "authority_impersonation", FBI_CN_POLICE, "通知：您涉嫌参与跨国金融诈骗，案件已移交公安机关。请勿告知家人，24小时内缴纳保证金以免被遣返回国。"),
("zh", S, "authority_impersonation", FCC_CN, "中国大使馆通知：您有一个包裹因涉嫌违法物品被扣留，请尽快联系 1-202-555-0188 处理，否则将承担法律责任。"),
("zh", S, "insurance_impersonation", FBI_CN_INS, "【医保理赔部】系统显示您近期在中国有一笔手术理赔申请，金额$8,600。如非本人申请，请回复1联系专员核实。"),
("zh", S, "toll_fee", FTC_TOLL, "E-ZPass提醒：您有未缴的过路费$4.35，请在24小时内付款以免产生$50滞纳金：https://ezpass-tollpay.top/zh"),
("zh", S, "package_fee", FTC_TOP, "【USPS】您的包裹因地址不完整无法投递，请在12小时内更新地址，否则将被退回：https://usps-redelivery.top/cn"),
("zh", S, "package_fee", FCC_PKG, "您的订单被海关扣留，需缴纳关税$2.99才能派送，请点击：https://bit.ly/3guanshui"),
("zh", S, "fake_fraud_alert", FTC_TOP, "【亚马逊】您的账户刚刚下单 iPhone 17 Pro，金额$1,249.00。如非本人操作，请立即致电 1-888-555-0143 取消订单。"),
("zh", S, "fake_fraud_alert", FTC_TOP, "【银行安全中心】检测到您的账户存在异常交易，资金面临风险。请立即致电 1-844-555-0199 将资金转入安全账户。"),
("zh", S, "bank_account_hold", FCC_GLOSS, "【中国银行】您的账户已被冻结，请立即登录 http://boc-cn-verify.cc 进行身份验证以解除冻结。"),
("zh", S, "job_task", FTC_TASK, "你好！我们公司招聘线上兼职，给APP点赞评分，日赚300-800美元，时间自由。有意请加WhatsApp +44 7700 900123"),
("zh", S, "job_task", FTC_TASK, "恭喜您！您的任务佣金已累计$1,480。为解锁提现，请先充值200 USDT完成最后一组任务。"),
("zh", S, "job_task", FTC_JOB26, "【亚马逊招聘】远程职位，每小时$120，无需经验。有兴趣请回复\"是\"获取详情。"),
("zh", S, "wrong_number", FTC_TOP, "王姐，明天上午10点的茶还约吗？我是瑜伽课的小琳。"),
("zh", S, "wrong_number", FTC_TOP, "不好意思发错了。不过你看起来人很好，我叫Lily，在新加坡做加密货币投资，可以交个朋友吗？"),
("zh", S, "fake_fraud_alert", FTC_TOP, "【PayPal】检测到您的账户在新设备登录。如非本人操作，请立即验证：paypa1-support.com/secure"),
("zh", S, "authority_impersonation", FBI_CN_POLICE, "留学生您好，您的签证信息被他人冒用开设银行账户，涉嫌刑事案件。请保持视频通话配合24小时监控调查，不要告诉任何人。"),
("zh", S, "package_fee", FTC_TOP, "【FedEx】您的包裹需支付$1.50重新派送费，单号US8823，请点击付款：fedx-delivery.com/fee"),
("zh", S, "bank_account_hold", FCC_GLOSS, "【微信支付】您的账户存在风险已被限制，请点击 wechatpay-safe.top 完成实名认证。"),
# ---------------- Chinese legit ----------------
("zh", L, "everyday", SELF, "我晚到十分钟，帮我占个座"),
("zh", L, "everyday", SELF, "妈，6点半能来接我训练吗？"),
("zh", L, "everyday", SELF, "周日去奶奶家吃饭，记得带蛋糕"),
("zh", L, "verification_code", SELF, "【微信】验证码：482913，用于登录验证，请勿泄露给他人。"),
("zh", L, "verification_code", SELF, "Your Google verification code is 731052. 请勿将验证码告诉任何人。"),
("zh", L, "appointment", SELF, "提醒：您预约的牙科检查在11月18日（周二）下午3:15，回复C确认。"),
("zh", L, "bank_alert", SELF, "【Chase】您的信用卡于11/14在TARGET消费$45.20。如非本人消费，请拨打卡背面的电话。"),
("zh", L, "delivery", SELF, "【亚马逊】您的包裹已送达，可在 amazon.com/orders 查看订单。"),
("zh", L, "school", SELF, "林肯中学通知：明天因教师培训，中午12:30提前放学。"),
("zh", L, "everyday", SELF, "化学实验报告写完了吗？第4题我不会"),
("zh", L, "everyday", SELF, "生日快乐！祝你天天开心"),
("zh", L, "everyday", SELF, "派对的地址发我一下"),
("zh", L, "bank_alert", SELF, "【Bank of America】您的工资$1,250.00已到账。"),
("zh", L, "work", SELF, "你好，我是图书馆的Sarah，你周六的班改到11点到3点，谢谢！"),
("zh", L, "everyday", SELF, "爷爷说暖气又坏了，你能给他打个电话吗？"),
("zh", L, "delivery", SELF, "【UPS】您的包裹预计今天下午2点至6点送达。查询：https://www.ups.com/track?tracknum=1Z999AA10123456784"),
("zh", L, "everyday", SELF, "好的，7点见"),
("zh", L, "everyday", SELF, "别忘了足球赛改到3号场地了"),
("zh", L, "pharmacy", SELF, "【CVS药房】您的处方药已可取，地址123 Main St。"),
("zh", L, "everyday", SELF, "到家了，谢谢你送我"),
]


def main():
    out = Path(__file__).with_name("scams2026.csv")
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "label", "language", "scam_type", "origin", "source_url", "notes"])
        for lang, label, stype, url, text in ROWS:
            w.writerow([text, label, lang, stype, "ai_written", url, ""])
    print(f"wrote {len(ROWS)} rows to {out}")


if __name__ == "__main__":
    main()
