#!/usr/bin/env python3
"""Prepara il sito per la pubblicazione: nuovo numero di versione, controllo aggiornamento nelle pagine
e link ai PDF/pagine con ?v=versione, così i browser non usano copie vecchie.
Da eseguire PRIMA di ogni commit: python3 _strumenti/stamp.py
(La cartella _strumenti non viene pubblicata da GitHub Pages.)"""
import os,re,time,json
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD=time.strftime('%Y%m%d%H%M%S')
open(os.path.join(ROOT,'version.json'),'w').write(json.dumps({"build":BUILD})+"\n")
SNIP='''<!--AGG--><script>
(function(){
 var B="%(b)s",t0=Date.now(),touched=false,last=0;
 ['click','keydown','touchstart'].forEach(function(e){addEventListener(e,function(){touched=true},{once:true,passive:true})});
 function banner(){
  if(document.getElementById('agg'))return;
  var d=document.createElement('div');d.id='agg';d.setAttribute('role','alert');
  d.style.cssText='position:fixed;left:0;right:0;bottom:0;z-index:99999;background:#b71c1c;color:#fff;padding:14px 16px;font:bold 18px Verdana,Arial,sans-serif;text-align:center';
  d.innerHTML='\\u00c8 disponibile una versione aggiornata. <button id="aggb" style="font:inherit;margin-left:8px;padding:8px 16px;border-radius:8px;border:2px solid #fff;background:#fff;color:#b71c1c;cursor:pointer">Aggiorna</button>';
  document.body.appendChild(d);document.getElementById('aggb').onclick=function(){go(true)};
 }
 function go(){
  fetch(location.href,{cache:'reload'}).then(function(){location.reload()},function(){location.reload()});
 }
 function check(){
  if(Date.now()-last<30000)return;last=Date.now();
  fetch("%(v)s?t="+Date.now(),{cache:'no-store'}).then(function(r){return r.json()}).then(function(v){
   if(!v||!v.build||v.build===B)return;
   var tried=false;try{tried=sessionStorage.getItem('agg_'+v.build)==='1'}catch(e){}
   if(!tried&&!touched&&Date.now()-t0<10000){try{sessionStorage.setItem('agg_'+v.build,'1')}catch(e){}go()}
   else banner();
  }).catch(function(){});
 }
 check();
 document.addEventListener('visibilitychange',function(){if(!document.hidden)check()});
})();
</script><!--/AGG-->'''
n=0
for dp,dirs,files in os.walk(ROOT):
    dirs[:]=[d for d in dirs if not d.startswith('.') and not d.startswith('_')]
    for f in files:
        if not f.endswith('.html'):continue
        p=os.path.join(dp,f);s=open(p,encoding='utf-8').read()
        rel=os.path.relpath(dp,ROOT);depth=0 if rel=='.' else len(rel.split(os.sep))
        vp='../'*depth+'version.json'
        s=re.sub(r'<!--AGG-->.*?<!--/AGG-->','',s,flags=re.S)
        sn=SNIP%{'b':BUILD,'v':vp}
        s=s.replace('</body>',sn+'</body>',1) if '</body>' in s else s+sn
        if 'http-equiv="Cache-Control"' not in s:
            s=s.replace('<head>','<head><meta http-equiv="Cache-Control" content="no-cache, must-revalidate">',1)
        s=re.sub(r'href="((?!https?:|mailto:|#)[^"?#]+\.(?:pdf|html))(?:\?v=\d+)?"',lambda m:'href="%s?v=%s"'%(m.group(1),BUILD),s)
        open(p,'w',encoding='utf-8').write(s);n+=1
print('versione',BUILD,'- pagine aggiornate:',n)
