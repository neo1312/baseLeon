window.onload=function(){

const consultaBtn=document.getElementById('consultar')
const date=document.getElementById('fecha')
const formVentas=document.getElementById('ventas')
const formCostoVentas=document.getElementById('costo')
const formMonederoUsado=document.getElementById('usado')
const formMonederoOtorgado=document.getElementById('otorgado')
const formPrimeraVenta=document.getElementById('primera')
const formUltimaVenta=document.getElementById('ultima')

	consultaBtn.addEventListener("click",(e)=>{
		e.preventDefault();
		let valorBtn=date.value
		traerData(valorBtn)
	})

	const traerData = (valorBtn)=>{
		let url = "/report/getdata"
		fetch(url,{
			method:'POST',
			headers:{
				'Content-Type':'application/json',
				'X-CSRFToken':csrftoken,	
			},
			body:JSON.stringify({'date':valorBtn})		
		})
		        .then((response)=>{
				return response.json();
			})
		        .then((data)=>{
				console.log('data',data)
				formVentas.value=(data.date[2])
				formCostoVentas.value=(data.date[3])
				formMonederoUsado.value=(data.date[0])
				formMonederoOtorgado.value=(data.date[1])
				formPrimeraVenta.value=(data.ventas[0])
				formUltimaVenta.value=(data.ventas[1])
			})

	}
}

