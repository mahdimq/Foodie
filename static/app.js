// const cuisines = [
// 	'african',
// 	'chinese',
// 	'japanese',
// 	'korean',
// 	'vietnamese',
// 	'thai',
// 	'indian',
// 	'british',
// 	'irish',
// 	'french',
// 	'italian',
// 	'mexican',
// 	'spanish',
// 	'middle eastern',
// 	'jewish',
// 	'american',
// 	'cajun',
// 	'southern',
// 	'greek',
// 	'german',
// 	'nordic',
// 	'eastern european',
// 	'caribbean',
// 	'latin american',
// ]
// const diets = ['pescetarian', 'lacto vegetarian', 'ovo vegetarian', 'vegan', 'vegetarian']
//

// const $recipeDisplay = $('#recipe-display')
// $(document).ready(searchRandomRecipes)
// // -----------------------------------------------------
// // ##### HTML TEMPLATE INDEX PAGE RANDOM RECIPES ######
// // -----------------------------------------------------
// function displayRecipes(response) {
// 	return `
// 		img src="${response.image}" class="card-img-top" alt="...">
// 		<div class="card-body">
// 			<h5 class="card-title">${response.title}</h5>
// 			<p class="card-text">${response.name}</p>
// 			<a href="#" class="btn btn-info">Go somewhere</a>
// 		</div>
// 	`
// }

$(document).ready(function () {
	loadItems()
})

async function loadItems() {
	const id = $(this).data('id')
	const query = $('#query')
	const diet = $('#diet')
	const cuisine = $('#cuisine')

	const res = await axios.get('/search', { params: { query, diet, cuisine } })
	console.log(res.data.data.results)
}
