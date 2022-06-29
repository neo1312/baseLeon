window.onload=function(){
//declaracion de variables y constantes
	
const btnOrder= document.getElementById('btnOrderList');

//crear nueva orden
btnOrder.addEventListener('click',(e)=>{
	createOrder()
})
    const createOrder = ()=>{
        let url = "/purchase/inicia"
        fetch(url,{
            method:'POST',
            headers:{
                'Content-Type':'application/json',
                'X-CSRFToken':csrftoken,
            }
        })
            .then((response)=>{
                return response.json();
            })
            .then((data)=>{
                console.log('data:',data)
            })
}
}
