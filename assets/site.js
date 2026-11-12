(function(){
  var b=document.querySelector('.menu'),s=document.getElementById('side');
  if(b&&s){b.addEventListener('click',function(){var o=s.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');});}
  Array.prototype.forEach.call(document.querySelectorAll('input[data-filter]'),function(inp){
    var prefix=inp.getAttribute('data-filter');
    var rows=Array.prototype.slice.call(document.querySelectorAll('table[id^="'+prefix+'"] tbody tr'));
    var out=document.querySelector('[data-count="'+prefix+'"]');
    function run(){var q=inp.value.trim().toLowerCase(),n=0;
      rows.forEach(function(r){var hit=!q||r.textContent.toLowerCase().indexOf(q)>-1;r.classList.toggle('hide',!hit);if(hit)n++;});
      if(out){out.textContent=q?(n+' of '+rows.length+' rows'):(rows.length+' rows');}}
    inp.addEventListener('input',run);run();
  });
  if(location.hash&&location.hash.indexOf('#row-')===0){var t=document.getElementById(location.hash.slice(1));
    if(t){var d=t.querySelector('details');if(d){d.open=true;}}}
})();
