from flask import Flask, request, render_template_string, redirect, session
import os, re, secrets, sqlite3
from datetime import datetime
app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY",secrets.token_hex(32))
DB=os.path.join(os.path.dirname(__file__),"bookings.db")
FLIGHTS=[
{"id":"SW101","from":"ACC","to":"LHR","depart":"06:25","arrive":"12:05","duration":"7h 40m","price":699},
{"id":"SW218","from":"ACC","to":"JFK","depart":"08:10","arrive":"14:50","duration":"9h 40m","price":749},
{"id":"SW337","from":"ACC","to":"DXB","depart":"10:35","arrive":"19:55","duration":"7h 20m","price":599},
{"id":"SW482","from":"ACC","to":"JNB","depart":"13:20","arrive":"20:05","duration":"5h 45m","price":429}]
CSS="""*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:#f5f7fb;color:#172033}.top{height:6px;background:linear-gradient(90deg,#d9272e 0 33%,#ffbf00 33% 66%,#1f4fbf 66%)}header{background:#fff;border-bottom:1px solid #e4e7ec}.nav,.inner,.container,.foot{max-width:1120px;margin:auto}.nav{height:70px;padding:0 20px;display:flex;align-items:center;justify-content:space-between}.brand{font-size:25px;font-weight:900;color:#183b72}.brand span{color:#d9272e}.links{display:flex;gap:25px;font-size:14px;font-weight:700}.btn{display:inline-block;border:0;border-radius:8px;padding:13px 18px;font-weight:900;cursor:pointer}.red{background:#d9272e;color:#fff}.outline{background:#fff;border:1px solid #d0d5dd}.hero{background:linear-gradient(120deg,#10264b,#294f91);color:#fff;padding:58px 20px 75px}.hero h1{font-size:45px;margin:0 0 10px}.hero p{opacity:.9;margin:0 0 28px}.search,.card,.flight,.form,.success{background:#fff;border:1px solid #e4e7ec;border-radius:13px;box-shadow:0 8px 25px #10182812}.search{padding:18px;color:#172033}.tabs{display:flex;gap:25px;border-bottom:1px solid #e4e7ec;margin-bottom:18px}.tab{padding:8px 3px 12px;font-size:13px;font-weight:900}.active{color:#d9272e;border-bottom:3px solid #d9272e}.grid{display:grid;grid-template-columns:1fr 1fr 1fr .65fr;gap:10px}.field,.input{width:100%;border:1px solid #d0d5dd;border-radius:8px;padding:12px;background:#fff;font-size:15px}.field label,.label{display:block;font-size:11px;color:#667085;font-weight:900;text-transform:uppercase;margin-bottom:5px}.field input,.field select{width:100%;border:0;outline:0;background:transparent;font-size:15px}.container{padding:38px 20px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.card{padding:22px}.route{font-size:23px;font-weight:900}.muted{color:#667085}.steps{display:flex;justify-content:center;gap:42px;margin-bottom:28px}.step{font-size:12px;font-weight:900;color:#98a2b3}.on{color:#d9272e}.results{display:grid;gap:14px}.flight{padding:20px;display:grid;grid-template-columns:1.35fr 1fr .65fr auto;align-items:center;gap:18px}.times{font-size:21px;font-weight:900}.routebar{display:flex;align-items:center;gap:9px;margin:8px 0}.routebar i{height:1px;background:#d0d5dd;flex:1}.pill{display:inline-block;padding:5px 9px;border-radius:20px;background:#eef2ff;color:#304cb2;font-size:11px;font-weight:900}.price{font-size:24px;font-weight:900}.form{max-width:760px;margin:auto;padding:28px}.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:15px}.full{grid-column:1/-1}.summary{background:#f8fafc;border:1px solid #e4e7ec;border-radius:9px;padding:17px;margin-bottom:18px}.total{display:flex;justify-content:space-between;border-top:1px solid #e4e7ec;padding-top:12px;margin-top:12px;font-weight:900}.notice{background:#fff7e6;border:1px solid #f6d48a;padding:12px;border-radius:8px;font-size:12px;color:#664d03;margin-bottom:18px} .success{padding:45px;text-align:center}.code{font-size:30px;font-weight:900;color:#304cb2;letter-spacing:2px;margin:20px}table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #e4e7ec}th,td{text-align:left;padding:12px;border-bottom:1px solid #e4e7ec;font-size:13px}.approve{background:#027a48;color:#fff;border:0;border-radius:6px;padding:8px;font-weight:900}.reject{background:#fff;color:#b42318;border:1px solid #efb0b4;border-radius:6px;padding:7px;font-weight:900}.actions{display:flex;gap:6px}@media(max-width:800px){.links{display:none}.hero h1{font-size:34px}.grid,.cards,.flight,.formgrid{grid-template-columns:1fr}.steps{gap:12px;flex-wrap:wrap}}"""
TPL="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{title}}</title><style>{{css|safe}}</style></head><body><div class="top"></div><header><nav class="nav"><a class="brand" href="/"><span>South</span>west</a><div class="links"><a href="/">Book</a><a href="/search">Flights</a><a href="/">Manage Trip</a><a href="/">Rewards</a></div><a class="btn outline" href="/monitor">Booking Monitor</a></nav></header>{{body|safe}}<footer><div class="foot"><b>Southwest</b><br>Independent airline booking interface. Not affiliated with any airline. Checkout accepts fictional/test payment information only; real card credentials, CVV, PINs and verification codes are not processed or stored.</div></footer></body></html>"""
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;c.execute("CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY AUTOINCREMENT,confirmation TEXT UNIQUE,name TEXT,email TEXT,origin TEXT,destination TEXT,depart TEXT,passengers INTEGER,amount REAL,last4 TEXT,status TEXT,created_at TEXT)");c.commit();return c
def get_booking(code):
 c=db();b=c.execute("SELECT * FROM bookings WHERE confirmation=?",(code,)).fetchone();c.close();return b
@app.get("/")
def home():
 body="""<section class="hero"><div class="inner"><h1>Travel farther. Fly smarter.</h1><p>Search flights and plan your next journey in a simple, modern booking experience.</p><form class="search" action="/search"><div class="tabs"><div class="tab active">ROUND TRIP</div><div class="tab">ONE WAY</div></div><div class="grid"><div class="field"><label>From</label><input name="origin" placeholder="City or airport" required></div><div class="field"><label>To</label><input name="destination" placeholder="City or airport" required></div><div class="field"><label>Depart</label><input name="depart" type="date" required></div><div class="field"><label>Passengers</label><select name="passengers">{% for n in range(1,7) %}<option>{{n}}</option>{% endfor %}</select></div></div><button class="btn red" style="width:100%;margin-top:14px">Search flights</button></form></div></section><section class="container"><h2>Popular destinations</h2><div class="cards"><div class="card"><div class="route">ACC → LHR</div><p class="muted">Accra to London</p><b>From &#36;699</b></div><div class="card"><div class="route">ACC → JFK</div><p class="muted">Accra to New York</p><b>From &#36;749</b></div><div class="card"><div class="route">ACC → DXB</div><p class="muted">Accra to Dubai</p><b>From &#36;599</b></div></div></section>"""
 return render_template_string(TPL,body=body,title="Southwest — Book flights",css=CSS)
@app.get("/search")
def search():
 origin=request.args.get("origin","");destination=request.args.get("destination","");depart=request.args.get("depart","");passengers=int(request.args.get("passengers","1"))
 body="""<main class="container"><div class="steps"><div class="step on">1. SELECT FLIGHT</div><div class="step">2. PASSENGERS</div><div class="step">3. PAYMENT</div><div class="step">4. CONFIRMATION</div></div><h1>Choose your flight</h1><p class="muted">{{origin}} → {{destination}}{% if depart %} • {{depart}}{% endif %} • {{passengers}} passenger(s)</p><div class="results">{% for f in flights %}<div class="flight"><div><span class="pill">NONSTOP</span><div class="routebar"><span class="times">{{f.depart}}</span><i></i><span class="times">{{f.arrive}}</span></div><span class="muted">{{f.duration}} • {{f.id}}</span></div><div><b>{{f['from']}} to {{f['to']}}</b><br><span class="muted">Direct service</span></div><div><div class="price">&#36;{{f.price}}</div><span class="muted">per passenger</span></div><div><a class="btn red" href="/checkout?flight={{f.id}}&depart={{depart}}&passengers={{passengers}}">Select</a></div></div>{% endfor %}</div></main>"""
 return render_template_string(TPL,body=body,title="Select a flight | Southwest",css=CSS,flights=FLIGHTS,origin=origin,destination=destination,depart=depart,passengers=passengers)
@app.get("/checkout")
def checkout():
 f=next((x for x in FLIGHTS if x["id"]==request.args.get("flight")),FLIGHTS[0]);p=int(request.args.get("passengers","1"));total=f["price"]*p
 body="""<main class="container"><div class="steps"><div class="step">1. SELECT FLIGHT</div><div class="step on">2. PASSENGERS & PAYMENT</div><div class="step">3. CONFIRMATION</div></div><div class="form"><h1>Complete your booking</h1><div class="summary"><b>{{f['from']}} → {{f['to']}}</b><br><span class="muted">{{f.depart}} – {{f.arrive}} • {{f.duration}} • {{f.id}}</span><div class="total"><span>Total</span><span>&#36;{{total}}.00</span></div></div><div class="notice"><b>Test payment only.</b> Use fictional/test payment values. No real card credentials are processed or stored.</div><form method="post" action="/submit"><input type="hidden" name="origin" value="{{f['from']}}"><input type="hidden" name="destination" value="{{f['to']}}"><input type="hidden" name="depart" value="{{request.args.get('depart','')}}"><input type="hidden" name="passengers" value="{{p}}"><input type="hidden" name="amount" value="{{total}}"><div class="formgrid"><div><label class="label">Passenger name</label><input class="input" name="name" required></div><div><label class="label">Email address</label><input class="input" type="email" name="email" required></div><div class="full"><label class="label">Test card number</label><input class="input" name="card" placeholder="4111 1111 1111 1111" required></div><div><label class="label">Expiration</label><input class="input" name="expiry" placeholder="MM/YY" required></div><div><label class="label">CVV (test)</label><input class="input" name="cvv" maxlength="4" placeholder="123" required></div><div class="full"><button class="btn red" style="width:100%">Continue to confirmation</button></div></div></form></div></main>"""
 return render_template_string(TPL,body=body,title="Checkout | Southwest",css=CSS,f=f,p=p,total=total,request=request)
@app.post("/submit")
def submit():
 name=request.form.get("name","").strip();email=request.form.get("email","").strip();card=re.sub(r"\D","",request.form.get("card",""))
 if not name or not email or len(card)<4:return redirect("/")
 code="SW"+secrets.token_hex(4).upper();c=db();c.execute("INSERT INTO bookings(confirmation,name,email,origin,destination,depart,passengers,amount,last4,status,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",(code,name,email,request.form.get("origin"),request.form.get("destination"),request.form.get("depart"),int(request.form.get("passengers","1")),float(request.form.get("amount","0")),card[-4:],"pending",datetime.utcnow().isoformat()));c.commit();c.close();return redirect("/confirmation/"+code)
@app.get("/confirmation/<code>")
def confirmation(code):
 b=get_booking(code)
 if not b:return "Booking not found",404
 body="""<main class="container"><div class="success"><span class="pill">BOOKING RECEIVED</span><h1>We're holding your booking</h1><p class="muted">Your booking has been submitted and is waiting for approval.</p><div class="code">{{b.confirmation}}</div><p><b>{{b.origin}} → {{b.destination}}</b><br>{{b.passengers}} passenger(s) • &#36;{{"%.2f"|format(b.amount)}}</p><a class="btn outline" href="/status/{{b.confirmation}}">Check booking status</a></div></main>"""
 return render_template_string(TPL,body=body,title="Booking received | Southwest",css=CSS,b=b)
@app.get("/status/<code>")
def status(code):
 b=get_booking(code)
 if not b:return "Booking not found",404
 if b["status"]=="approved":return redirect("/ticket/"+code)
 body="""<main class="container"><div class="success"><span class="pill">STATUS</span><h1>Booking {{b.status.title()}}</h1><p>Confirmation: <b>{{b.confirmation}}</b></p><p class="muted">{{b.origin}} → {{b.destination}} • {{b.passengers}} passenger(s)</p><a class="btn outline" href="/status/{{b.confirmation}}">Refresh status</a></div></main>"""
 return render_template_string(TPL,body=body,title="Booking status | Southwest",css=CSS,b=b)
@app.get("/ticket/<code>")
def ticket(code):
 b=get_booking(code)
 if not b:return "Booking not found",404
 if b["status"]!="approved":return redirect("/status/"+code)
 body="""<main class="container"><div class="success"><span class="pill">CONFIRMED</span><h1>Booking confirmed</h1><div class="code">{{b.confirmation}}</div><h2>{{b.origin}} → {{b.destination}}</h2><p>{{b.name}}<br>{{b.passengers}} passenger(s)</p><p class="muted">Test payment reference •••• {{b.last4}}</p><button class="btn red" onclick="window.print()">Print confirmation</button></div></main>"""
 return render_template_string(TPL,body=body,title="Confirmation | Southwest",css=CSS,b=b)
def authorized():return bool(session.get("monitor_auth"))
@app.route("/monitor",methods=["GET","POST"])
def monitor():
 password=os.environ.get("MONITOR_PASSWORD")
 if request.method=="POST" and password and secrets.compare_digest(request.form.get("password",""),password):session["monitor_auth"]=True;return redirect("/monitor")
 if not authorized():
  note="" if password else "<div class='notice'>MONITOR_PASSWORD has not been configured on the server yet.</div>"
  body=f"""<main class="container"><div class="form"><h1>Booking Monitor</h1><p class="muted">Authorized staff access only.</p>{note}<form method="post"><label class="label">Monitor password</label><input class="input" type="password" name="password" required><button class="btn red" style="width:100%;margin-top:14px">Sign in</button></form></div></main>"""
  return render_template_string(TPL,body=body,title="Booking Monitor | Southwest",css=CSS)
 c=db();rows=c.execute("SELECT * FROM bookings ORDER BY id DESC").fetchall();c.close()
 body="""<main class="container"><h1>Booking Monitor</h1><p class="muted">Review bookings. Payment information is test-only and limited to the last four digits.</p><table><tr><th>Confirmation</th><th>Passenger</th><th>Route</th><th>Amount</th><th>Payment</th><th>Status</th><th>Action</th></tr>{% for b in rows %}<tr><td><b>{{b.confirmation}}</b></td><td>{{b.name}}<br><span class="muted">{{b.email}}</span></td><td>{{b.origin}} → {{b.destination}}</td><td>&#36;{{"%.2f"|format(b.amount)}}</td><td>TEST •••• {{b.last4}}</td><td><b>{{b.status.upper()}}</b></td><td>{% if b.status=="pending" %}<div class="actions"><form method="post" action="/approve/{{b.confirmation}}"><button class="approve">Approve</button></form><form method="post" action="/reject/{{b.confirmation}}"><button class="reject">Reject</button></form></div>{% endif %}</td></tr>{% endfor %}</table></main>"""
 return render_template_string(TPL,body=body,title="Booking Monitor | Southwest",css=CSS,rows=rows)
@app.post("/approve/<code>")
def approve(code):
 if not authorized():return redirect("/monitor")
 c=db();c.execute("UPDATE bookings SET status='approved' WHERE confirmation=?",(code,));c.commit();c.close();return redirect("/monitor")
@app.post("/reject/<code>")
def reject(code):
 if not authorized():return redirect("/monitor")
 c=db();c.execute("UPDATE bookings SET status='rejected' WHERE confirmation=?",(code,));c.commit();c.close();return redirect("/monitor")
@app.get("/logout")
def logout():session.clear();return redirect("/monitor")
@app.get("/health")
def health():return {"status":"ok"}
db().close()
