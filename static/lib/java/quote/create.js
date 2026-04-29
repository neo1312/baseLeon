window.onload=function(){

const formDetalle=document.getElementById("formDetalle")
const formQuantity= document.getElementById('quantity')
const formselectCodigo = document.getElementById('codigo')
const formselectProduct= document.getElementById('selectProduct')
const formunitario= document.getElementById('unitario')
const formtotal= document.getElementById('total')
const cuerpoTabla=document.getElementById('cuerpoTabla')
const btnCart= document.getElementById("btnCart")
const btnAdd= document.getElementById("btnAdd")
const inputDetalle = document.getElementsByClassName("detalle")
const totalFactura = document.getElementById("totalFactura")
const input = document.getElementById('buscador')
const autocomplete_result= document.getElementById('autocomplete-result')
const quote_id = document.getElementById('quote_id') ? document.getElementById('quote_id').value : null

//traer datos de producto.
btnCart.addEventListener("click",(e)=>{
    e.preventDefault();
    let valorBtn=input.value
    traerData(valorBtn)
    input.value=""

})

const traerData = (valorBtn)=>{
    let url = "/quote/getdata"
    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'id':valorBtn, 'quote_id':quote_id})
    })
        .then((response)=>{
            return response.json();
        })
        .then((data)=>{
            console.log('data',data)
            arrayData=data.datos
            formselectProduct.value=arrayData[1]
            formselectCodigo.value=arrayData[0]
            formunitario.value=arrayData[2]
            formQuantity.value= 1
        })
    
}

//resgistrar orderItems
btnAdd.addEventListener("click",(e)=>{
    e.preventDefault();
    quantity= document.getElementById("quantity")
    let codigo= document.getElementById("codigo")
    codigo=codigo.value
    quantity=quantity.value
    registrarItem(codigo,quantity)
    formDetalle.reset()
})


const registrarItem= (codigo,quantity)=>{
 console.log("heeeY")
    let url = "/quote/itemview"
    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify([codigo,quantity,quote_id])
    })
        .then((response)=>{
            return response.json();
        })
        .then((data)=>{
            console.log(data)
            datos=data
            if (typeof datos === 'object'){
                if (datos.warning){
                    console.warn(datos.warning)
                    alert(datos.warning)
                }
            }
            location.reload()
        })
}
