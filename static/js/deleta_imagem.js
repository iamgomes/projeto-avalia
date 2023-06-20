function deleta_imagem(id){
    console.log(id);
    $.ajax({
        type:"GET",
        url : `/questionarios/imagem/${id}/delete/`,
        data:{
            id:id //id get from button delete
        },
        success:function(data){ //when success will reload page after 3 second
            console.log('Apagado!');
            $('#mensagem').text('Imagem removida!!!')
            $(`#imagem-thumb-${id}`).remove();
        }
        });
}