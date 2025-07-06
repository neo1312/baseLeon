window.onload=function(){

const consultaBtn=document.getElementById('consultar')
const date=document.getElementById('fecha')
const formventasBrutas=document.getElementById('ventasBrutas')
const devoluciones=document.getElementById('devoluciones')
const ventasNetas=document.getElementById('ventasNetas')
const costoBruto=document.getElementById('costoBruto')
const costoDev=document.getElementById('costoDev')
const costoNeto=document.getElementById('costoNeto')
const monederoUsado=document.getElementById('monederoUsado')
const monederoOtorgado=document.getElementById('monederoOtorgado')
const total_value=document.getElementById('total_value')

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
				formventasBrutas.value=(data.date[1])
				devoluciones.value=(data.date[5])
				ventasNetas.value=(data.date[3])
				costoBruto.value=(data.date[2])
				costoDev.value=(data.date[7])
				costoNeto.value=(data.date[4])
				monederoUsado.value=(data.date[0])
				monederoOtorgado.value=(data.date[10])
				total_value.value=(data.date[11])
			})

	}
}

