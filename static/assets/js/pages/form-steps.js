function(){
    $("#example-basic").steps({
        headerTag: "h3",
        bodyTag: "section",
        transitionEffect: "fade",
        autoFocus: true,
        labels: {
            finish: "Enviar",
            next: "Próximo",
            previous: "Anterior"
        }
    })
};
