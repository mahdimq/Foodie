const recipeDisplay = $('#recipe-display')
// const favForm = $('#favorites-form')
const addLikeBtn = $('.fav')
const pageUl = $('#page-ul')

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
		// const res = await axios.delete(`/api/favorite/${id}`)
		// $(e.target).toggleClass('fas fa-heart')
		// $(e.target).toggleClass('far fa-heart')
		console.log('DELETE METHOD')
	}
}

// async function handlePageRequest(e) {
// 	e.preventDefault()

// 	console.log(e.target)
// 	console.log($(e.target).text())

// axios.get to the search route, provide value as parameter
// res.data, use that JSON data to populate the page, DOM manipulation (first clear the container from old data)
// }
recipeDisplay.on('click', addLikeBtn, handleFavorite)

// pageUl.on('click', '.page-link', handlePageRequest)

// async function loadItems() {
// 	const id = $(this).data('id')
// 	const query = $('#query')
// 	const diet = $('#diet')
// 	const cuisine = $('#cuisine')

// 	const res = await axios.get('/api')
// 	return res
// }
