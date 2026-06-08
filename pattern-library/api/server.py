#!/usr/bin/env python3
"""OperAI Pattern Library API on port 18830"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json, glob, os
PDIR = "/root/aurelio-v2/operai/pattern-library/patterns"
SFILE = "/root/aurelio-v2/operai/pattern-library/stats.json"

def load_yaml(fp):
    d = {}; cf = None
    with open(fp) as f:
        for l in f:
            s = l.strip()
            if not s or s.startswith("#"): continue
            if ":" in s and not s.startswith("-"):
                k,v = s.split(":",1); k=k.strip(); v=v.strip().strip('"').strip("|")
                if v.startswith("["): d[k]=[x.strip().strip('"') for x in v.strip("[]").split(",") if x.strip()]
                elif not v: cf=k; d[k]=""
                else: d[k]=v; cf=None
            elif s.startswith("- ") and cf:
                d.setdefault(cf,[])
                if isinstance(d[cf],str): d[cf]=[]
                d[cf].append(s[2:].strip().strip('"'))
            elif cf and s and isinstance(d.get(cf),str): d[cf]+=" "+s
    return d

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        p=self.path.rstrip("/")
        if p=="/health": self.r(200,{"ok":True,"service":"operai-pattern-library"})
        elif p=="/stats": self.r(200,json.load(open(SFILE)) if os.path.exists(SFILE) else {"total":0})
        elif p=="/patterns":
            ps=[]
            for dd in sorted(glob.glob(f"{PDIR}/*")):
                if not os.path.isdir(dd) or os.path.basename(dd).startswith("_"): continue
                for f in sorted(glob.glob(f"{dd}/*.yaml")):
                    y=load_yaml(f); ps.append({k:y.get(k,"") for k in ["id","domain","title","type","confidence","tags"]})
            self.r(200,{"count":len(ps),"patterns":ps})
        elif p.startswith("/patterns/"):
            dom=p.split("/")[2]; dd=os.path.join(PDIR,dom)
            if not os.path.isdir(dd): self.r(404,{"error":"not found"}); return
            self.r(200,{"domain":dom,"patterns":[load_yaml(f) for f in sorted(glob.glob(f"{dd}/*.yaml"))]})
        else: self.send_error(404)
    def r(self,c,d):
        self.send_response(c); self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
        self.wfile.write(json.dumps(d,indent=2).encode())
    def log_message(self,*a): pass

if __name__=="__main__":
    s=HTTPServer(("0.0.0.0",18830),H); print("Pattern Library API :18830"); s.serve_forever()
