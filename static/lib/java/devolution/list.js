window.onload=function(){
//declaracion de variables y constantes
	
const btnOrder= document.getElementById('btnOrderList');
const clientId= document.getElementById('clientId');
const btnMonedero= document.getElementById('btnMonedero');

//crear nueva orden
btnOrder.addEventListener('click',(e)=>{
	createOrder()
})
    const createOrder = ()=>{
	let client=clientId.value
	let monedero=btnMonedero.value
        let url = "/devolution/inicia"
        fetch(url,{
            method:'POST',
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
                console.log('data:',data)
            })
}
}
