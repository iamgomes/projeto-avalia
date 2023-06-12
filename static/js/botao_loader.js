btn = document.querySelector(".btn-loader"),
btn.onclick = function(){
    this.form.submit();
    this.innerHTML = "<span class='spinner-border spinner-border-sm' role='status' aria-hidden='true'></span>";
    this.disabled=true;
    setTimeout(() => {
        this.innerHTML = 'Salvo'
    }, timeout);
};
