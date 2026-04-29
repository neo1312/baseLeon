window.onload=function(){
const clientId = document.getElementById('clientId');
const btnOrder = document.getElementById('btnOrderList');
const btnMonedero = document.getElementById('btnMonedero');
const tipoVenta = document.getElementById('tipoVenta');


btnOrder.addEventListener('click',(e)=>{
	e.preventDefault();
  	if (!clientId.value) {
            clientId.value = '1'; // Set default value to '1' (mostrador client)
        }
	console.log("client id from button click:")
	console.log(clientId.value)
	console.log(btnMonedero.value)
	console.log(tipoVenta.value)
	let client = clientId.value;
	let monedero = btnMonedero.value;
	let tipo = tipoVenta.value;
	let url = "/devolution/inicia"
	
	fetch(url,{
		method:"POST",
		headers:{
			'Content-Type':'application/json',
            		'X-CSRFToken':csrftoken,
			},
		body:JSON.stringify({'id':client,'monedero':monedero,'tipo':tipo})
    			   })
		.then((response)=>{
			return response.json();
			})
		.then((data)=>{
			console.log(data)
			arrayData=data.datos
			console.log(arrayData)
			const devolutionId = arrayData
			window.location.href = `/devolution/create/${devolutionId}/`
			})
				      })
			}		

