window.onload=function(){
//declaracion de variables y constantes
	
const btnOrder= document.getElementById('btnOrderList');
const clientId= document.getElementById('clientId');
const btnMonedero= document.getElementById('btnMonedero');
const tipoVenta = document.getElementById('tipoVenta');

//crear nueva orden
btnOrder.addEventListener('click',(e)=>{
	createOrder()
})
    const createOrder = ()=>{
	if (!clientId.value) {
            clientId.value = '1'; // Set default value to '1' (mostrador client)
        }
	let client=clientId.value
	let monedero=btnMonedero.value
	let tipo=tipoVenta.value
        let url = "/devolution/inicia"
        fetch(url,{
            method:'POST',
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
                console.log('data:',data)
		const devolutionId = data.datos
		window.location.href = `/devolution/create/${devolutionId}/`
            })
}
}
