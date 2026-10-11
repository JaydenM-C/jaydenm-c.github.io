/* Blog page: date / topic views, and in the topic view a filter to one
   topic (see _pages/blog.html). State lives in the address so it can be
   shared: ?view=topic for all topics, #tag-name for one topic. */
(function () {
  var sw = document.querySelector('.view-switch');
  if (!sw) return;
  var views = document.querySelectorAll('.blog-view');
  var viewButtons = sw.querySelectorAll('.view-switch__btn');
  var chipsRow = document.querySelector('.topic-chips');
  var chips = chipsRow ? chipsRow.querySelectorAll('.topic-chip') : [];
  var groups = document.querySelectorAll('.topic-group');

  function setAddress(view, topic) {
    var url = new URL(window.location.href);
    url.searchParams.delete('view');
    url.hash = '';
    if (topic) url.hash = topic;
    else if (view === 'topic') url.searchParams.set('view', 'topic');
    history.replaceState(null, '', url);
  }

  function filter(topic) {
    groups.forEach(function (g) { g.hidden = !!topic && g.id !== topic; });
    chips.forEach(function (c) { c.setAttribute('aria-pressed', c.dataset.topic === (topic || '')); });
  }

  function show(view, topic, updateAddress) {
    views.forEach(function (v) { v.hidden = v.dataset.view !== view; });
    viewButtons.forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.view === view); });
    if (chipsRow) chipsRow.hidden = view !== 'topic';
    filter(view === 'topic' ? topic : '');
    if (updateAddress) setAddress(view, view === 'topic' ? topic : '');
  }

  viewButtons.forEach(function (b) {
    b.addEventListener('click', function () { show(b.dataset.view, '', true); });
  });
  chips.forEach(function (c) {
    c.addEventListener('click', function () { show('topic', c.dataset.topic, true); });
  });

  // initial state: a tag in the address wins, then ?view=, then date
  var hash = decodeURIComponent(window.location.hash.slice(1));
  var known = hash && document.getElementById(hash) && document.getElementById(hash).classList.contains('topic-group');
  var param = new URL(window.location.href).searchParams.get('view');
  show(known || param === 'topic' ? 'topic' : 'date', known ? hash : '', false);
  sw.hidden = false;
  // the browser jumps to #tag on load; the filtered list should start at the top
  if (known) {
    window.scrollTo(0, 0);
    window.addEventListener('load', function () { window.scrollTo(0, 0); });
  }
})();
