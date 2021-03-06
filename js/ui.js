window.onload = function () {
  var viewAll = localStorage.getItem('viewAll') == 'true';
  var highlightNew = localStorage.getItem('highlightNew') == 'true';
  window.toggleViewAll.innerText = viewAll ? '한국어판만 보기' : '모두 보기';
  window.toggleHighlightNew.innerText = highlightNew ? '강조 끄기' : '신규 항목 강조';

  window.barButton.onclick = function() {
    toggleViewSelector('ul.barItem', 'block');
  }

  window.toggleViewAll.onclick = function() {
    toggleViewSelector('.tde, .tic, .starter');
    viewAll = !viewAll;
      window.toggleViewAll.innerText = viewAll ? '한국어판만 보기' : '모두 보기';
    localStorage.setItem('viewAll', viewAll);
  }

  window.toggleHighlightNew.onclick = function() {
    toggleViewColor('.V1_2');
    highlightNew = !highlightNew;
    window.toggleHighlightNew.innerText = highlightNew ? '강조 끄기' : '신규 항목 강조';
    localStorage.setItem('highlightNew', highlightNew);
  }

  var viewSelector = document.querySelectorAll('.scenarioToggleButton');
  viewSelector.forEach(function (x) {
    x.onclick = function() {
      x.innerText = x.innerText == '내용 보기' ? '내용 가리기' : '내용 보기';
      toggleView(window[x.id.replace('Toggle', 'Div')], 'display', 'block');
    };
  });

  if (!viewAll) {
    toggleViewSelector('.tde, .tic, .starter');
  }

  if (highlightNew) {
    toggleViewColor('.V1_2');
  }
}

function toggleView (element, type, mode, initial) {
  if (!mode) {
    mode = '';
  }
  if (!initial) {
    initial = 'none';
  }
  element.style[type] = element.style[type] === mode ? initial : mode;
}

function toggleViewSelector (selector, mode) {
  var viewSelector = document.querySelectorAll(selector);
  viewSelector.forEach(function (x) {
    toggleView(x, 'display', mode);
  });
}

function toggleViewColor (selector, color) {
  var viewSelector = document.querySelectorAll(selector);
  viewSelector.forEach(function (x) {
    toggleView(x, 'color', '', 'red');
  });
}
