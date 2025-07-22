window.onload=function(){
const clientId = document.getElementById('clientId');
const btnOrder = document.getElementById('btnOrderList');
const btnMonedero = document.getElementById('btnMonedero');


btnOrder.addEventListener('click',(e)=>{
	e.preventDefault();
  	if (!clientId.value) {
            clientId.value = '1'; // Set default value to '1' (mostrador client)
        }
	console.log("client id from button click:")
	console.log(clientId.value)
	console.log(btnMonedero.value)
	let client = clientId.value;
	let monedero = btnMonedero.value;
	let url = "/sale/inicia"
	
	fetch(url,{
		method:"POST",
		headers:{
			'Content-Type':'application/json',
            		'X-CSRFToken':csrftoken,
			},
	   	body:JSON.stringify({'id':client,'monedero':monedero})
    			   })
		.then((response)=>{
			return response.json();
			})
		.then((data)=>{
			console.log(data)
			arrayData=data.datos
			console.log(arrayData)
			const saleId = arrayData
			window.location.href = `http://134.209.74.186:8000/sale/create/${saleId}/`
			})
				      })
			}		

