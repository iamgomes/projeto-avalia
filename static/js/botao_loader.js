btn = document.querySelector(".btn-loader"),

btn.onclick = function(){
    this.form.submit();
    this.innerHTML = "<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>";
    this.disabled=true;
    setTimeout(() => {
        this.innerHTML = 'Salvo'
    }, timeout);
};


function botao_atribuir(button){

    btn = document.getElementById('botao_atribuir')
    btn.innerHTML = "<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>";
    btn.disabled=true;

    // Cria um novo campo de input para armazenar o valor do botão clicado
    input = document.createElement('input');
    input.setAttribute('type', 'hidden');
    input.setAttribute('name', 'acao');
    input.setAttribute('value', button);

    // Adiciona o campo de input ao formulário
    btn.form.appendChild(input);

    // Submete o formulário
    btn.form.submit();

    setTimeout(() => {
        btn.innerHTML = 'Salvo'
    }, timeout);
};

function botao_tramitar(button){

    btn = document.getElementById('botao_tramitar')
    btn.innerHTML = "<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>";
    btn.disabled=true;

    // Cria um novo campo de input para armazenar o valor do botão clicado
    input = document.createElement('input');
    input.setAttribute('type', 'hidden');
    input.setAttribute('name', 'acao');
    input.setAttribute('value', button);

    // Adiciona o campo de input ao formulário
    btn.form.appendChild(input);

    // Submete o formulário
    btn.form.submit();

    setTimeout(() => {
        btn.innerHTML = 'Salvo'
    }, timeout);
};