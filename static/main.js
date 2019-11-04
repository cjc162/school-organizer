window.onload = function() {
	chcekDueDates();
}

function chcekDueDates() {
	var inputs = document.getElementsByClassName("due_date");
	var today = new Date();

	var i;
	for (i = 0; i < inputs.length; i++) {
		due_date = new Date(inputs[i].innerText);

	  	if (due_date.setDate(due_date.getDate() + 1) < today) {
	  		inputs[i].style.background = "red"
	  	} else if (due_date.setDate(due_date.getDate() - 3) < today) {
	  		inputs[i].style.background = "yellow"
	  	}

	}
}
