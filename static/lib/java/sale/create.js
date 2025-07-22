window.onload=function(){

const formDetalle=document.getElementById("formDetalle")
const formQuantity= document.getElementById('quantity')
const formselectCodigo = document.getElementById('codigo')
const formselectProduct= document.getElementById('selectProduct')
const formunitario= document.getElementById('unitario')
const formtotal= document.getElementById('total')
const cuerpoTabla=document.getElementById('cuerpoTabla')
const btnCart= document.getElementById("btnCart")
const inputDetalle = document.getElementsByClassName("detalle")
const totalFactura = document.getElementById("totalFactura")
const input = document.getElementById('buscador')
const autocomplete_result= document.getElementById('autocomplete-result')



//traer datos de producto.
btnCart.addEventListener("click",(e)=>{
    e.preventDefault();
    let valorBtn=input.value
    traerData(valorBtn)
    input.value=""

})

const traerData = (valorBtn)=>{
    let url = "/sale/getdata"
    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'id':valorBtn})
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
    let url = "/sale/itemview"
    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify([codigo,quantity])
    })
        .then((response)=>{
            return response.json();
        })
        .then((data)=>{
            console.log(data)
		datos=data
		if (datos =='No hay stock suficiente'){
			alert('No hay suficiente stock')
		}
		else{
			console.log('hubo errooor')
			location.reload()
		} 
        })
}

//delete sale items
document.querySelectorAll('.deleteButton').forEach(button => {
	button.addEventListener('click', function (){
		const itemId = this.getAttribute('data-item-id');
		console.log(itemId)

		fetch(`/sale/itemdelete/${itemId}/`,{
			method: 'DELETE',
			headers:{
			'Content-Type':'application/json',
            		'X-CSRFToken':csrftoken,
			}
		})
		.then(response => response.json())
			.then(data => {
				if(data.success){
				alert (data.message);
				document.getElementById(`item-${itemId}`).remove();
				totalFactura.value = data.cart_total
				}else{
					alert(data.message || "failed");
				}
			})
			})
})
}
