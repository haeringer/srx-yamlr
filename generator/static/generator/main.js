
function objectSearch(s) {
    var input, filter, ul, li, a, i;
    input = document.getElementById(s.id);
    filter = input.value.toUpperCase();
    ul = document.getElementById(s.id + 'Ul');
    li = ul.getElementsByTagName('li');

    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName('a')[0];
        if (a.innerHTML.toUpperCase().indexOf(filter) > -1 && filter.length >= 1) {
            $(ul).removeClass('d-none');
            li[i].style.display = '';
        } else {
            li[i].style.display = 'none';
        }
    }
}