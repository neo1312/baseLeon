window.onload=function(){

const consultaBtn=document.getElementById('consultar')
const date=document.getElementById('fecha')

	consultaBtn.addEventListener("click",(e)=>{
		e.preventDefault();
		let valorBtn=date.value
		traerData(valorBtn)
		input.value=""
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

	}
}

