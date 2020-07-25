// ############# CAROUSEL ############

// ################################################

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
const $recipeDisplay = $('#recipe-display')
$(document).ready(searchRandomRecipes)
// -----------------------------------------------------
// ##### HTML TEMPLATE INDEX PAGE RANDOM RECIPES ######
// -----------------------------------------------------
function displayRecipes(response) {
	return `
		img src="${response.image}" class="card-img-top" alt="...">
		<div class="card-body">
			<h5 class="card-title">${response.title}</h5>
			<p class="card-text">${response.name}</p>
			<a href="#" class="btn btn-info">Go somewhere</a>
		</div>
	`
}

const display = document.querySelector('#recipe-display')
const searchBtn = document.querySelector('#search')

// ########### DISPLAY RANDOM RECIPES ################

async function searchRandomRecipes() {
	const offset = 0
	const res = await axios.get('/', { params: { offset } })
	if (res.data.data.results.length !== 0) {
		res.data.data.results.forEach((recipe) => {
			let recipes = displayRecipes(recipe)
			$recipeDisplay.append(recipes)
			console.log(recipe)
		})
	} else {
		console.log('CHECK FOR ERRORS')
	}
}
