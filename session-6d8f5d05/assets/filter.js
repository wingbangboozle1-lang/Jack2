// Table filter for session-6d8f5d05 dashboard
document.querySelectorAll('table').forEach(function(t) {
  var input = document.createElement('input');
  input.type = 'search';
  input.placeholder = 'Filter rows\u2026';
  input.style.cssText = 'width:100%;padding:8px;margin:8px 0;border:1px solid #ddd;border-radius:6px;font-size:14px';
  t.parentNode.insertBefore(input, t);
  input.addEventListener('input', function() {
    var q = input.value.toLowerCase();
    t.querySelectorAll('tbody tr').forEach(function(r) {
      r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });
});
