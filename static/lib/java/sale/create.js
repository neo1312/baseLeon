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
    const saleId = document.getElementById('sale_id').value;
    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify({'id':valorBtn, 'sale_id': saleId})
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
 console.log("Adding item to cart")
    let url = "/sale/itemview"
    const saleId = document.getElementById('sale_id').value;
    fetch(url,{
        method:'POST',
        headers:{
            'Content-Type':'application/json',
            'X-CSRFToken':csrftoken,
        },
        body:JSON.stringify([codigo, quantity, saleId])
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

// increment quantity
document.querySelectorAll('.incrementBtn').forEach(button => {
	button.addEventListener('click', function(e) {
		e.preventDefault();
		const itemId = this.getAttribute('data-item-id');
		updateItemQuantity(1 , 'increment');
	})
})

// decrement quantity
document.querySelectorAll('.decrementBtn').forEach(button => {
	button.addEventListener('click', function(e) {
		e.preventDefault();
		const itemId = this.getAttribute('data-item-id');
		updateItemQuantity(itemId, 'decrement');
	})
})

const updateItemQuantity = (itemId, action) => {
	let url = "/sale/itemupdate/"
	fetch(url, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': csrftoken,
		},
		body: JSON.stringify({'item_id': itemId, 'action': action})
	})
	.then(response => response.json())
	.then(data => {
		console.log(data);
		if(data.success) {
			if(data.deleted) {
				// Item was deleted because quantity reached 0
				const itemRow = document.getElementById(`item-${itemId}`);
				if(itemRow) {
					itemRow.remove();
				}
				// Update cart total
				totalFactura.value = parseFloat(data.cart_total).toFixed(2);
			} else {
				// Update quantity display in the table
				const qtyDisplay = document.getElementById(`qty-${itemId}`);
				if(qtyDisplay) {
					qtyDisplay.textContent = data.quantity;
				}
				
				// Update item total (precioUnitario is stored, need to calculate)
				const row = document.getElementById(`item-${itemId}`);
				if(row) {
					const precioUnitario = parseFloat(row.cells[2].textContent);
					const newTotal = (precioUnitario * data.quantity).toFixed(2);
					row.cells[3].textContent = newTotal;
				}
				
				// Update cart total
				totalFactura.value = parseFloat(data.cart_total).toFixed(2);
			}
		} else {
			alert('Error: ' + (data.error || 'Unknown error'));
		}
	})
	.catch(error => {
		console.error('Error:', error);
		alert('Failed to update quantity');
	})
}
}
