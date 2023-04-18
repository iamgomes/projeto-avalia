function delete_questionario(id) { 
    Swal.fire({
        title: 'Você tem certeza?',
        text: "Esta ação não poderá ser revertida.",
        icon: 'warning',
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#0f9cf3',
        cancelButtonColor: '#f32f53',
        confirmButtonText: 'Sim, excluir!'
    }).then((result) => {
    if (result.value) {
        Swal.fire({
        title: 'Excluído!',
        text: 'O registro foi excluído com sucesso.',
        icon: 'success',
        showConfirmButton: false
        });
        $.ajax({
        type:"GET",
        url : `/questionarios/${id}/delete/`,
        data:{
            id:id //id get from button delete
        },
        success:function(data){ //when success will reload page after 3 second
            window.setTimeout( function(){ 
                location.reload();
            }, 1000 );
        }
        });
    }
    })
}

function envia_para_validacao(id) { 
    Swal.fire({
        title: 'Tudo pronto?',
        text: "Após o envio para validação, você não poderá mais editar as respostas.",
        icon: 'question',
        showCancelButton: true,
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#0f9cf3',
        cancelButtonColor: '#f32f53',
        confirmButtonText: 'Sim, enviar!'
    }).then((result) => {
    if (result.value) {
        Swal.fire({
        title: 'Enviada!',
        text: 'Esta avaliação foi enviada para validação. Aguarde!',
        icon: 'success',
        showConfirmButton: false
        });
        $.ajax({
        type:"GET",
        url : `/avaliacoes/${id}/envia_para_validacao/`,
        data:{
            id:id //id get from button delete
        },
        success:function(data){ //when success will reload page after 3 second
            window.setTimeout( function(){ 
                location.reload();
            }, 1000 );
        }
        });
    }
    })
}