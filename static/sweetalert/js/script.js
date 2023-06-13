function delete_questionario(id) { 
    Swal.fire({
        title: `Você tem certeza?`,
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
        text: 'O questionário foi excluído com sucesso.',
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


function delete_validacao(id) { 
    Swal.fire({
        title: `Você tem certeza?`,
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
        text: 'A validação foi excluído com sucesso.',
        icon: 'success',
        showConfirmButton: false
        });
        $.ajax({
        type:"GET",
        url : `/validacoes/${id}/delete/`,
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


function delete_usuario(id) { 
    Swal.fire({
        title: `Você tem certeza?`,
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
        text: 'O usuário foi excluído com sucesso.',
        icon: 'success',
        showConfirmButton: false
        });
        $.ajax({
        type:"GET",
        url : `/usuarios/${id}/delete/`,
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