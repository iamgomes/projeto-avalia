function menos_link(el){
    document.getElementById(el).remove();

}

function add_link(el, id){
    let cont = 0;
    container = document.getElementById(el)

    html = `<div class='row' id='link-${cont}'> <div class='col-md'> <div class='input-group'><input name='link-${id}' type='url' placeholder='https://example.com' class='form-control mt-2'> <a onclick=menos_link('link-${id}') class='btn btn-danger waves-effect waves-light mt-2' data-toggle='tooltip' title='Excluir Link'><i class='mdi mdi-link-variant-remove mt-2'></i></a></div>  </div>  </div> </div>`

    container.innerHTML += html
    cont++
}


function MudarEstado(el) {
    var display = document.getElementById(el).style.display;
    if(display == "block")
        document.getElementById(el).style.display = 'none';
    else
        document.getElementById(el).style.display = 'block';
}
