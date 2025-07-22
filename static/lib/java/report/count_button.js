window.onload=function(){

console.log("JavaScript file is loaded!");

const new_button=document.getElementById('new')
const name_var=document.getElementById('name')
const id_var=document.getElementById('id')
const barcode_var=document.getElementById('barcode')
const stock_var=document.getElementById('stock')
const count_var=document.getElementById('count')
const btn_save=document.getElementById('save')
const counter_num=document.getElementById('counter')
const costo=document.getElementById('costo')
let counter =0 

	new_button.addEventListener("click",(e)=>{
		e.preventDefault();
		counter++;
		if (counter > 20) counter = 1;
		counter_num.textContent =  counter;
		traerData(new_button)
	})

	const traerData = (new_button)=>{
		fetch('/report/counter_view')
			.then(response =>{
				if(!response.ok){
					throw new error('Network response was not ok');
					
				}
				return response.json();
				
			})
			.then(data =>{
				console.log(data)
				if(data.name){
				name_var.value=data.name
				id_var.value=data.id
				barcode_var.value=data.barcode
				stock_var.value=data.stock
				costo.value=data.costo
				}
				else{
								name_var.value="Error getting data"
				}

				
			})
			.catch(error =>{
				console.error("tehere wa a problem",error);
				
			})
			

	}

	btn_save.addEventListener("click",(e)=>{
		e.preventDefault();
		let count=count_var.value
		let id=id_var.value
		update_stock(count,id)
		alert(" Stock updated successfully!")
	})

	const update_stock= (count,id)=>{
		let url = "/report/update_stock"
		fetch(url,{
			method:'POST',
			headers:{
				'Content-Type':'application/json',
				'X-CSRFToken':csrftoken,	
			},
			body:JSON.stringify({'stock':count,'id':id})		
		})
		        .then((response)=>{
				return response.json();
			})
		        .then((data)=>{
				console.log('data',data)
			})

	}


}

