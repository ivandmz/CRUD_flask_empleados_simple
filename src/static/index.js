const btnsConfirm = document.querySelectorAll("#btnBorrar")

if (btnsConfirm.length) {                           //podria ser btnsConfirm.length >=1 pero es lo mismo porque aca seria VoF
    for (const btn of btnsConfirm){
        btn.addEventListener("click", event =>{
            const resp = confirm("Esta opción no tiene marcha atrás. ¿Confirma?")
            if (!resp) event.preventDefault()       //este event.prevent... deberia ir entre {} pero como es una sola sentencia se pude obviar...
        })
    }
}