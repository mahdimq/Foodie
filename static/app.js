const recipeDisplay = $('#recipe-display')
const addLikeBtn = $('.fav')
const print = $('#print')
// const recipeDetailsDisplay = $('#recipe-details')

// add and remove favorites
recipeDisplay.on('click', '.fav', handleFavorite)

// Print recipe details
print.on('click', handlePrint)

// show recipe details
// recipeDisplay.on('click', '.show-recipe', showRecipe)

async function handleFavorite(e) {
	e.preventDefault()
	const id = $(e.target).parent().data('id')
	console.log(id)

	if (e.target.classList.contains('fas')) {
		await axios.delete(`/api/favorite/${id}`)
		$(e.target).toggleClass('fas fa-heart')
		$(e.target).toggleClass('far fa-heart')
		console.log('DELETE METHOD')
	} else {
		await axios.post(`/api/favorite/${id}`, (data = { id: id }))
		$(e.target).toggleClass('fas fa-heart')
		$(e.target).toggleClass('far fa-heart')
		console.log('ADD METHOD')
	}
}

// Handle print function
function handlePrint(e) {
	e.preventDefault()
	window.print()
}
