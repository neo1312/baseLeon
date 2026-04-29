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

//traer datos de producto.
btnCart.addEventListener("click",(e)=>{
    e.preventDefault();
    let valorBtn=input.value
    traerData(valorBtn)
    input.value=""

})

const traerData = (valorBtn)=>{
    let url = "/devolution/getdata"
    const devolutionId = document.getElementById('devolution_id').value;
    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'id':valorBtn, 'devolution_id': devolutionId})
    })
        .then((response)=>{
            return response.json();
        })
        .then((data)=>{
            console.log('data',data)
            if (data.error) {
                alert(data.error)
                return
            }
            arrayData=data.datos
            formselectProduct.value=arrayData[1]
            formselectCodigo.value=arrayData[0]
            formunitario.value=arrayData[2]
            formQuantity.value= 1
        })
        .catch((error) => {
            console.error('Error:', error)
            alert('Failed to fetch product data')
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
 console.log("Adding item to cart")
     let url = "/devolution/itemview"
     const devolutionId = document.getElementById('devolution_id').value;
     fetch(url,{
         method:'POST',
         headers:{
             'Content-Type':'application/json',
             'X-CSRFToken':csrftoken,
         },
         body:JSON.stringify([codigo, quantity, devolutionId])
     })
         .then((response)=>{
             return response.json();
         })
         .then((data)=>{
             console.log(data)
             if (data === 'No hay stock suficiente'){
                 alert('No hay suficiente stock')
             }
             else if (data.success){
                 // Successfully added, reload to get updated items and totals
                 location.reload()
             }
             else {
                 alert('Error adding item')
             }
         })
         .catch((error) => {
             console.error('Error:', error)
             alert('Failed to add item')
         })
}

//delete devolution items
document.querySelectorAll('.deleteButton').forEach(button => {
	button.addEventListener('click', function (){
		const itemId = this.getAttribute('data-item-id');
		console.log(itemId)

		fetch(`/devolution/itemdelete/${itemId}/`,{
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
