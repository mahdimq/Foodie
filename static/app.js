const recipeDisplay = $('#recipe-display')
const addLikeBtn = $('.fav')
const recipeDetailsDisplay = $('#recipe-details')
const pageUl = $('#page-ul')

recipeDisplay.on('click', '.fav', handleFavorite)
recipeDisplay.on('click', '.show-recipe', showRecipe)

async function showRecipe(e) {
	e.preventDefault()
	const id = $(e.target).data('id')
	const res = await axios.get(`/recipes/${id}`)
	recipeDetailsDisplay.empty()
	let details = showDetails(res.data)
	recipeDetailsDisplay.append(details)

	// if you want to show it without refreshing the page, send an axios.get request to get the data for the id
	// then you would clear the current main contents of the page
	// write DOM manipulation code to create and show the elements for the recipe show page
}

async function handleFavorite(e) {
	e.preventDefault()
	const id = $(e.target).parent().data('id')
	console.log(id)

	if (!e.target.classList.contains('fav')) {
		const res = await axios.post(`/api/favorite/${id}`, (data = { id: id }))
		$(e.target).toggleClass('fas fa-heart')
		$(e.target).toggleClass('far fa-heart')
		console.log('ADD METHOD', res)
	} else {
		const res = await axios.delete(`/api/favorite/${id}`)
		// $(e.target).toggleClass('fas fa-heart')
		// $(e.target).toggleClass('far fa-heart')
		console.log('DELETE METHOD')
	}
}

// function showRecipeHTML(recipe, favorites) {
// 	let favButton

// 	if (favorites.includes(recipe.id)) {
// 		favButton = `<button style="float: right;" id="${recipe.id}" data-id="${recipe.id}" class='fav btn btn-sm'><i class="fas fa-heart fa-2x"></i></button>`
// 	} else {
// 		favButton = `<button style="float: right;" id="${recipe.id}" data-id="${recipe.id}" class='fav btn btn-sm'><i class="far fa-heart fa-2x"></i></button>`
// 	}

// 	return `
// <div class="col-xs-12 col-sm-6 col-md-6 col-lg-5 col-xl-4 my-2">
//         <div class="card ui fluid card" style="width: 100%;">
//           <img src="${recipe.image}" class="card-img-top" alt="${recipe.title}">
//           <div class="card-body">
//             <h5 class="card-label">${recipe.title}</h5>
//             <div class="card-body">
//               <p class="card-text my-0">Ready in: ${recipe.readyInMinutes} minutes</p>
//               <p class="card-text my-0">Serves: ${recipe.servings}</p>
//               <a href="${recipe.sourceUrl}" target="_blank" class="card-text mb-1 d-block text-center"><small
//                   class="text-muted">${recipe.sourceName}</small></a>
//             </div>
//             <a class="btn btn-info" href='/recipe/${recipe.id}'>Show Recipe</a>

//            <form id="favorites-form" class="d-inline" methods='POST'>
//             ${favButton}
//             </form>
//           </div>
//         </div>
//       </div>
//     `
// }

// async function handlePageRequest(e) {
// 	e.preventDefault()

// 	console.log(e.target)
// 	console.log($(e.target).text())

// axios.get to the search route, provide value as parameter
// res.data, use that JSON data to populate the page, DOM manipulation (first clear the container from old data)
// }

// pageUl.on('click', '.page-link', handlePageRequest)

// async function loadItems() {
// 	const id = $(this).data('id')
// 	const query = $('#query')
// 	const diet = $('#diet')
// 	const cuisine = $('#cuisine')

// 	const res = await axios.get('/api')
// 	return res
// }

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
