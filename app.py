from flask import Flask, request, render_template_string, redirect, session
import os, re, secrets, sqlite3, json
from datetime import datetime
app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY",secrets.token_hex(32))
DB=os.path.join(os.path.dirname(__file__),"bookings.db")
AIRPORTS=[
{"code":"ACC","name":"Kotoka International Airport","city":"Accra","country":"Ghana"},
{"code":"LHR","name":"Heathrow Airport","city":"London","country":"United Kingdom"},
{"code":"JFK","name":"John F. Kennedy International Airport","city":"New York","country":"United States"},
{"code":"DXB","name":"Dubai International Airport","city":"Dubai","country":"United Arab Emirates"},
{"code":"JNB","name":"O.R. Tambo International Airport","city":"Johannesburg","country":"South Africa"},
{"code":"ATL","name":"Hartsfield-Jackson Atlanta International Airport","city":"Atlanta","country":"United States"},
{"code":"CDG","name":"Charles de Gaulle Airport","city":"Paris","country":"France"},
{"code":"FRA","name":"Frankfurt Airport","city":"Frankfurt","country":"Germany"},
{"code":"AMS","name":"Amsterdam Airport Schiphol","city":"Amsterdam","country":"Netherlands"},
{"code":"IST","name":"Istanbul Airport","city":"Istanbul","country":"Türkiye"},
{"code":"DOH","name":"Hamad International Airport","city":"Doha","country":"Qatar"},
{"code":"LOS","name":"Murtala Muhammed International Airport","city":"Lagos","country":"Nigeria"}
]
FLIGHTS=[
{"id":"SW101","from":"ACC","to":"LHR","depart":"06:25","arrive":"12:05","duration":"7h 40m","price":699},
{"id":"SW218","from":"ACC","to":"JFK","depart":"08:10","arrive":"14:50","duration":"9h 40m","price":749},
{"id":"SW337","from":"ACC","to":"DXB","depart":"10:35","arrive":"19:55","duration":"7h 20m","price":599},
{"id":"SW482","from":"ACC","to":"JNB","depart":"13:20","arrive":"20:05","duration":"5h 45m","price":429}]
CSS="""*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Inter,Arial,sans-serif;background:#f6f7f9;color:#172033}.top{height:5px;background:#d9272e}header{background:#fff;border-bottom:1px solid #e5e7eb;position:sticky;top:0;z-index:20}.nav,.inner,.container,.foot{max-width:1180px;margin:auto}.nav{height:72px;padding:0 22px;display:flex;align-items:center;gap:34px}.brand{font-size:26px;font-weight:950;color:#183b72;text-decoration:none;letter-spacing:-1px}.brand span{color:#d9272e}.links{display:flex;gap:26px;font-size:14px;font-weight:800;flex:1}.links a{color:#26364f;text-decoration:none}.links a:hover{color:#d9272e}.btn{display:inline-block;border:0;border-radius:6px;padding:13px 19px;font-weight:900;cursor:pointer;text-decoration:none}.red{background:#d9272e;color:#fff}.red:hover{background:#b91f25}.outline{background:#fff;border:1px solid #cbd2dc;color:#172033}.hero{min-height:570px;background-image:linear-gradient(90deg,rgba(7,27,57,.82),rgba(7,27,57,.25)),url('https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1800&q=85');background-size:cover;background-position:center;color:#fff;padding:76px 22px 110px}.hero h1{font-size:52px;line-height:1.05;letter-spacing:-2px;margin:0 0 14px;max-width:680px}.hero p{font-size:18px;line-height:1.5;max-width:620px;margin:0 0 34px}.search{max-width:1120px;padding:20px;color:#172033;background:#fff;border-radius:8px;box-shadow:0 18px 50px #0005}.tabs{display:flex;gap:30px;border-bottom:1px solid #e4e7ec;margin-bottom:18px}.tab{padding:7px 2px 13px;font-size:13px;font-weight:900}.active{color:#d9272e;border-bottom:3px solid #d9272e}.grid{display:grid;grid-template-columns:1fr 1fr 1fr .7fr;gap:10px}.field,.input{width:100%;border:1px solid #cbd2dc;border-radius:5px;padding:13px;background:#fff;font-size:15px}.field label,.label{display:block;font-size:11px;color:#667085;font-weight:900;text-transform:uppercase;margin-bottom:5px}.field input,.field select{width:100%;border:0;outline:0;background:transparent;font-size:15px}.container{padding:42px 22px}.section-title{display:flex;justify-content:space-between;align-items:end;margin-bottom:20px}.section-title h2{margin:0;font-size:28px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.card{background:#fff;border:1px solid #e4e7ec;border-radius:8px;overflow:hidden;box-shadow:0 5px 18px #1018280d}.card-img{height:180px;background-size:cover;background-position:center}.card-body{padding:18px}.route{font-size:21px;font-weight:950}.muted{color:#667085}.card-body p{margin:6px 0 14px}.steps{display:flex;justify-content:center;gap:48px;margin-bottom:30px}.step{font-size:12px;font-weight:900;color:#98a2b3}.on{color:#d9272e}.results{display:grid;gap:14px}.flight{padding:19px;background:#fff;border:1px solid #e1e5eb;border-radius:8px;display:grid;grid-template-columns:1.4fr 1fr .65fr auto;align-items:center;gap:18px;box-shadow:0 4px 15px #1018280b}.times{font-size:22px;font-weight:900}.routebar{display:flex;align-items:center;gap:9px;margin:8px 0}.routebar i{height:1px;background:#cbd2dc;flex:1}.pill{display:inline-block;padding:5px 9px;border-radius:3px;background:#eef2ff;color:#304cb2;font-size:11px;font-weight:900}.price{font-size:24px;font-weight:950}.form{max-width:760px;margin:auto;padding:30px;background:#fff;border:1px solid #e1e5eb;border-radius:8px;box-shadow:0 8px 25px #10182810}.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:15px}.full{grid-column:1/-1}.summary{background:#f8fafc;border:1px solid #e4e7ec;border-radius:6px;padding:17px;margin-bottom:18px}.total{display:flex;justify-content:space-between;border-top:1px solid #e4e7ec;padding-top:12px;margin-top:12px;font-weight:900}.hidden{display:none!important}.passenger-panel{border:1px solid #e1e5eb;border-radius:8px;padding:20px;background:#fff}.passenger-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px;gap:10px}.passenger-number{font-size:14px;font-weight:950;color:#172033;letter-spacing:.4px}.notice{background:#fff7e6;border:1px solid #f6d48a;padding:12px;border-radius:6px;font-size:12px;color:#664d03;margin-bottom:18px}.success{padding:50px;text-align:center;background:#fff;border:1px solid #e1e5eb;border-radius:8px;box-shadow:0 8px 25px #10182810}.code{font-size:30px;font-weight:900;color:#304cb2;letter-spacing:2px;margin:20px}table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #e4e7ec}th,td{text-align:left;padding:12px;border-bottom:1px solid #e4e7ec;font-size:13px}.approve{background:#027a48;color:#fff;border:0;border-radius:5px;padding:8px;font-weight:900}.reject{background:#fff;color:#b42318;border:1px solid #efb0b4;border-radius:5px;padding:7px;font-weight:900}.actions{display:flex;gap:6px}footer{background:#12233e;color:#dbe4f0;padding:32px 22px;line-height:1.7;font-size:12px}.foot{max-width:1180px}@media(max-width:800px){.links{display:none}.nav{height:64px}.hero{min-height:auto;padding:55px 18px 80px}.hero h1{font-size:38px}.grid,.cards,.flight,.formgrid{grid-template-columns:1fr}.search{padding:15px}.steps{gap:12px;flex-wrap:wrap}.container{padding:30px 16px}.card-img{height:160px}}"""
TPL="""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{title}}</title><style>{{css|safe}}</style></head><body><div class="top"></div><header><nav class="nav"><a class="brand" href="/"><span>South</span>west</a><div class="links"><a href="/">Book</a><a href="/search">Flights</a><a href="/">Manage Trip</a><a href="/">Rewards</a></div><a class="btn outline" href="/monitor">Booking Monitor</a></nav></header>{{body|safe}}<footer><div class="foot"><b>Southwest</b><br>Independent airline booking interface. Not affiliated with any airline. Checkout accepts fictional/test payment information only; real card credentials, CVV, PINs and verification codes are not processed or stored.</div></footer></body></html>"""
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
 c.execute("CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY AUTOINCREMENT,confirmation TEXT UNIQUE,name TEXT,email TEXT,origin TEXT,destination TEXT,depart TEXT,passengers INTEGER,amount REAL,last4 TEXT,status TEXT,created_at TEXT)")
 cols={row[1] for row in c.execute("PRAGMA table_info(bookings)").fetchall()}
 if "passenger_details" not in cols:c.execute("ALTER TABLE bookings ADD COLUMN passenger_details TEXT")
 c.commit();return c
def get_booking(code):
 c=db();b=c.execute("SELECT * FROM bookings WHERE confirmation=?",(code,)).fetchone();c.close();return b
@app.get("/")
def home():
 body="""<section class="hero"><div class="inner"><h1>Book your next trip with confidence.</h1><p>Compare routes, choose your flight and complete your booking in one simple experience.</p><form class="search" action="/search"><div class="tabs"><div class="tab active">ROUND TRIP</div><div class="tab">ONE WAY</div><div class="tab">MULTI-CITY</div></div><div class="grid"><div class="field"><label>From</label><input name="origin" class="airport-input" list="airport-list" autocomplete="off" placeholder="City, airport or code" required></div><div class="field"><label>To</label><input name="destination" class="airport-input" list="airport-list" autocomplete="off" placeholder="City, airport or code" required></div><datalist id="airport-list">{% for a in airports %}<option value="{{a.code}}">{{a.city}} — {{a.name}}, {{a.country}}</option><option value="{{a.city}}">{{a.code}} — {{a.name}}, {{a.country}}</option>{% endfor %}</datalist><div class="field"><label>Depart</label><input name="depart" type="date" required></div><div class="field"><label>Passengers</label><select name="passengers">{% for n in range(1,7) %}<option>{{n}}</option>{% endfor %}</select></div></div><button class="btn red" style="width:100%;margin-top:14px">Search flights</button></form></div></section><section class="container"><div class="section-title"><h2>Popular destinations</h2><span class="muted">Explore our available routes</span></div><div class="cards"><article class="card"><div class="card-img" style="background-image:url('https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=900&q=80')"></div><div class="card-body"><div class="route">ACC → LHR</div><p class="muted">Accra to London</p><b>From &#36;699</b></div></article><article class="card"><div class="card-img" style="background-image:url('https://images.unsplash.com/photo-1485871981521-5b1fd3805eee?auto=format&fit=crop&w=900&q=80')"></div><div class="card-body"><div class="route">ACC → JFK</div><p class="muted">Accra to New York</p><b>From &#36;749</b></div></article><article class="card"><div class="card-img" style="background-image:url('https://images.unsplash.com/photo-1512453979798-5ea266f8880c?auto=format&fit=crop&w=900&q=80')"></div><div class="card-body"><div class="route">ACC → DXB</div><p class="muted">Accra to Dubai</p><b>From &#36;599</b></div></article></div></section>"""
 return render_template_string(TPL,body=body,title="Southwest — Book flights",css=CSS,airports=AIRPORTS)
@app.get("/search")
def search():
 origin=request.args.get("origin","").strip();destination=request.args.get("destination","").strip();depart=request.args.get("depart","");passengers=int(request.args.get("passengers","1"))
 def airport_code(value):
  v=value.lower()
  for a in AIRPORTS:
   if v in (a["code"].lower(),a["city"].lower(),a["name"].lower()):return a["code"]
  return value.upper()
 origin=airport_code(origin);destination=airport_code(destination)
 body="""<main class="container"><div class="steps"><div class="step on">1. SELECT FLIGHT</div><div class="step">2. PASSENGERS</div><div class="step">3. PAYMENT</div><div class="step">4. CONFIRMATION</div></div><h1>Choose your flight</h1><p class="muted">{{origin}} → {{destination}}{% if depart %} • {{depart}}{% endif %} • {{passengers}} passenger(s)</p><div class="results">{% for f in flights %}<div class="flight"><div><span class="pill">NONSTOP</span><div class="routebar"><span class="times">{{f.depart}}</span><i></i><span class="times">{{f.arrive}}</span></div><span class="muted">{{f.duration}} • {{f.id}}</span></div><div><b>{{f['from']}} to {{f['to']}}</b><br><span class="muted">Direct service</span></div><div><div class="price">&#36;{{f.price}}</div><span class="muted">per passenger</span></div><div><a class="btn red" href="/checkout?flight={{f.id}}&depart={{depart}}&passengers={{passengers}}">Select</a></div></div>{% endfor %}</div></main>"""
 return render_template_string(TPL,body=body,title="Select a flight | Southwest",css=CSS,flights=FLIGHTS,origin=origin,destination=destination,depart=depart,passengers=passengers)
@app.get("/checkout")
def checkout():
 f=next((x for x in FLIGHTS if x["id"]==request.args.get("flight")),None)
 if not f:return redirect("/")
 try:p=max(1,min(6,int(request.args.get("passengers","1"))))
 except:p=1
 total=f["price"]*p
 body="""<main class="container"><div class="steps"><div class="step on">1. SELECT FLIGHT</div><div class="step on">2. PASSENGERS</div><div class="step">3. PAYMENT</div><div class="step">4. CONFIRMATION</div></div><div class="form"><h1>Passenger details</h1><p class="muted">Enter the details for every passenger before payment.</p><div class="summary"><b>{{f['from']}} → {{f['to']}}</b><br><span class="muted">{{f.depart}} – {{f.arrive}} • {{f.duration}} • {{f.id}}</span><div class="total"><span>{{p}} passenger{% if p != 1 %}s{% endif %}</span><span>&#36;{{total}}.00</span></div></div><div class="notice"><b>Passenger information</b><br>Complete each passenger one at a time. Use Next Passenger to move forward, then continue to payment after the final passenger.</div><form method="post" action="/submit" id="bookingForm"><input type="hidden" name="origin" value="{{f['from']}}"><input type="hidden" name="destination" value="{{f['to']}}"><input type="hidden" name="depart" value="{{request.args.get('depart','')}}"><input type="hidden" name="passengers" value="{{p}}"><input type="hidden" name="amount" value="{{total}}">{% for n in range(1,p+1) %}<section class="passenger-panel{% if n != 1 %} hidden{% endif %}" data-passenger="{{n}}"><div class="passenger-head"><span class="passenger-number">PASSENGER {{n}} OF {{p}}</span><span class="pill">{% if n == 1 %}PRIMARY PASSENGER{% else %}TRAVELER{% endif %}</span></div><div class="formgrid"><div class="full"><label class="label">Full name</label><input class="input passenger-required" name="passenger_name_{{n}}" placeholder="Enter passenger {{n}} full name" {% if n == 1 %}required{% endif %}></div><div><label class="label">Email address{% if n != 1 %} (optional){% endif %}</label><input class="input" type="email" name="passenger_email_{{n}}" placeholder="name@example.com" {% if n == 1 %}required{% endif %}></div><div><label class="label">Date of birth</label><input class="input" type="date" name="passenger_dob_{{n}}" {% if n == 1 %}required{% endif %}></div></div>{% if n < p %}<button type="button" class="btn red next-passenger" data-next="{{n+1}}" style="width:100%;margin-top:18px">Next passenger →</button>{% else %}<div style="margin-top:20px"><h2 style="margin-bottom:8px">Payment</h2><p class="muted" style="font-size:13px">Test payment only. Do not enter real card credentials.</p><div class="formgrid"><div class="full"><label class="label">Test card number</label><input class="input passenger-required" name="card" placeholder="4111 1111 1111 1111" required></div><div><label class="label">Expiration</label><input class="input passenger-required" name="expiry" placeholder="MM/YY" required></div><div><label class="label">CVV (test)</label><input class="input passenger-required" name="cvv" maxlength="4" placeholder="123" required></div></div><button class="btn red" style="width:100%;margin-top:18px">Continue to confirmation</button></div>{% endif %}</section>{% endfor %}</form></div></main><script>
document.querySelectorAll(".next-passenger").forEach(function(btn){
 btn.addEventListener("click",function(){
   const current=btn.closest(".passenger-panel");
   const required=current.querySelector(".passenger-required");
   if(!required.value.trim()){required.reportValidity();return;}
   current.classList.add("hidden");
   const next=document.querySelector('[data-passenger="'+btn.dataset.next+'"]');
   if(next) next.classList.remove("hidden");
   window.scrollTo({top:0,behavior:"smooth"});
 });
});
</script>"""
 return render_template_string(TPL,body=body,title="Passenger details | Southwest",css=CSS,f=f,p=p,total=total,request=request)
@app.post("/submit")
def submit():
 name=request.form.get("passenger_name_1","").strip() or request.form.get("name","").strip()
 email=request.form.get("passenger_email_1","").strip() or request.form.get("email","").strip()
 card=re.sub(r"\D","",request.form.get("card",""))
 if not name or not email or len(card)<4:return redirect("/")
 try:passengers=max(1,min(6,int(request.form.get("passengers","1"))))
 except:passengers=1
 passenger_details=[]
 for n in range(1,passengers+1):
  passenger_details.append({"number":n,"name":request.form.get(f"passenger_name_{n}","").strip(),"email":request.form.get(f"passenger_email_{n}","").strip(),"dob":request.form.get(f"passenger_dob_{n}","").strip()})
 code="SW"+secrets.token_hex(4).upper();c=db();c.execute("INSERT INTO bookings(confirmation,name,email,origin,destination,depart,passengers,amount,last4,status,created_at,passenger_details) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(code,name,email,request.form.get("origin"),request.form.get("destination"),request.form.get("depart"),passengers,float(request.form.get("amount","0")),card[-4:],"pending",datetime.utcnow().isoformat(),json.dumps(passenger_details)));c.commit();c.close();return redirect("/confirmation/"+code)
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
 c=db();raw_rows=c.execute("SELECT * FROM bookings ORDER BY id DESC").fetchall();c.close()
 rows=[]
 for b in raw_rows:
  try: passenger_list=json.loads(b["passenger_details"] or "[]")
  except: passenger_list=[{"number":1,"name":b["name"],"email":b["email"],"dob":""}]
  item=dict(b);item["passenger_list"]=passenger_list;rows.append(item)
 body="""<main class="container"><h1>Booking Monitor</h1><p class="muted">Review all passenger information submitted with each booking. Payment details are test-only; full card numbers, CVV and expiration are never stored or displayed.</p><div class="results">{% for b in rows %}<section class="card" style="padding:20px"><div class="section-title"><div><span class="pill">{{b.confirmation}}</span><h2 style="margin:10px 0 4px">{{b.origin}} → {{b.destination}}</h2><span class="muted">{{b.depart}} • {{b.passengers}} passenger(s)</span></div><b>{{b.status.upper()}}</b></div><div style="overflow:auto"><table><tr><th>Passenger</th><th>Full name</th><th>Email</th><th>Date of birth</th></tr>{% for p in b.passenger_list %}<tr><td>Passenger {{p.number}}</td><td>{{p.name}}</td><td>{{p.email or "—"}}</td><td>{{p.dob or "—"}}</td></tr>{% endfor %}</table></div><p><b>Total:</b> &#36;{{"%.2f"|format(b.amount)}} &nbsp; <b>Payment:</b> TEST •••• {{b.last4}}</p>{% if b.status=="pending" %}<div class="actions"><form method="post" action="/approve/{{b.confirmation}}"><button class="approve">Approve</button></form><form method="post" action="/reject/{{b.confirmation}}"><button class="reject">Reject</button></form></div>{% endif %}</section>{% endfor %}</div></main>"""

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
