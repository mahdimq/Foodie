// searchForm.addEventListener('submit', showRecipes)

// Handle Show recipe
async function showRecipe(e) {
	e.preventDefault()
	const id = $(e.target).data('id')
	const res = await axios.get(`/recipes/${id}`)
	recipeDetailsDisplay.empty()
	let details = showDetails(res.data)
	recipeDetailsDisplay.append(details)
}

// Populate HTML for RECIPE DETAILS
function showDetails(data) {
	let name = data.analyzedInstructions.map((n) => `<p>${n.name}</p>`).join('')
	let steps = data.analyzedInstructions.map((s) => `<p>${s.steps.step}</p>`).join('')
	console.log(steps)
	let ingredients = data.extendedIngredients.map((i) => `<p>${i.original}</p>`).join('')
	// let instructions = data.instructions
	// 	.split('.')
	// 	.map((s) => `<P>${s}</P>`)
	// 	.join('')

	return `
	<div class="container">
	 <div style="opacity: 0.9;" class="jumbotron mt-4">

	<h1 class="display-3 text-info">${data.title}</h1>

		<hr>
		<div class="row justify-content-center">

			<div class="col-md-6 col-lg-8 mt-2">
				<img class="recipe-img" src="${data.image}" alt="${data.title}">
				<small><a href="${data.sourceUrl}" class="text-muted text-center text-uppercase">Recipe from
						${data.sourceName}</a></small>
			</div>

			<div class="col-md-6 col-lg-4 mt-2">
				<div class="info-list">
					<ul>

						<li class="lead my-1">Ready in: ${data.readyInMinutes} minutes</li>

						<li class="lead my-1">Serves: ${data.servings}</li>
					</ul>
					<div>


						<ul>
							${data.vegetarian ? "<li class='text-info'>Vegetarian</li>" : ''}
							${data.vegan ? "<li class='text-info'>Vegan</li>" : ''}
							${data.glutenFree ? "<li class='text-info'>Gluten Free</li>" : ''}
							${data.dairyFree ? "<li class='text-info'>Dairy Free</li>" : ''}
							${data.sustainable ? "<li class='text-info'>Sustainable</li>" : ''}
							${data.ketogenic ? "<li class='text-info'>Ketogenic</li>" : ''}
							${data.whole30 ? "<li class='text-info'>Whole30</li>" : ''}
					 </ul>

						<hr>

						<ul>
							${data.veryHealthy ? "<li><i class='fas fa-heartbeat text-danger'></i> Healthy</li>" : ''}
							${data.veryPopular ? "<li><i class='fas fa-fire text-warning'></i> Popular</li>" : ''}
						</ul>

					</div>
				</div>
			</div>



			<div class="col-md-6 col-lg-5">
				<h3 class="text-center recipe-subtitle">Ingredients</h3>
				<ul class="list-group list-group-flush text-center">
				${ingredients}
				<br>
				</ul>
			</div>


			<div class="col-md-6 col-lg-7">
			<h3 class="text-center recipe-subtitle">Steps</h3>
			<ul class="list-group list-group-flush text-center">
				${name ? name : ''}

				${
					steps
						? steps
						: `<p class="">Sorry!</p><p class="">Unable find any instructions for this recipe!</p>`
				}

				</ul>
			</div>
		</div>
		</div>
		</div>
		`
}
