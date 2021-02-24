var usernameField = document.querySelector('#usernameField')
var feedbackField = document.querySelector('.invalid_feedback');
var emailField = document.querySelector("#emailField")
var emailFeedback = document.querySelector('.invalid_email')
var usernameSuccess = document.querySelector('.username-success')
var showPasswordToggle = document.querySelector('.showPasswordToggle')
var passwordField = document.querySelector('#passwordField')
var submitBtn = document.querySelector('.submit-btn')

const handleToggleInput=(e)=>{
    if(showPasswordToggle.textContent==="SHOW"){
        showPasswordToggle.textContent="HIDE";
        passwordField.setAttribute("type","text");
    }else{
        showPasswordToggle.textContent="SHOW";
        passwordField.setAttribute("type","password");
    }
}

showPasswordToggle.addEventListener('click',handleToggleInput);

emailField.addEventListener("keyup",(e) => {
    console.log("777",777);
    const emailVal = e.target.value;

    if(emailVal.length>0){
        fetch("/authentication/validate-email", {
            body:JSON.stringify({ email:emailVal }),
            method:"POST",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log("data",data);
            if(data.email_error){
                emailField.classList.add("is-invalid");
                emailFeedback.style.display = "block";
                emailFeedback.innerHTML = `<p>${data.email_error}</p>`;
                submitBtn.disabled = true;
            }else{
                submitBtn.removeAttribute("disabled");
                emailField.classList.remove("is-invalid");
                emailFeedback.style.display = "none";
            }
        });
    }
})

usernameField.addEventListener("keyup",(e)=> {
    console.log("777",777);
    const usernameVal = e.target.value;

    if(usernameVal.length>0){
        usernameSuccess.style.display="block";
        usernameSuccess.textContent=`Checking ${usernameVal}`
        fetch("/authentication/validate-username", {
            body:JSON.stringify({ username:usernameVal }),
            method:"POST",
        })
        .then((res) => res.json())
        .then((data) => {
            console.log("data",data);
            usernameSuccess.style.display="none";
            if(data.username_error){
                usernameField.classList.add("is-invalid");
                feedbackField.style.display = "block";
                feedbackField.innerHTML = `<p>${data.username_error}</p>`;
                submitBtn.disabled=true;
            }else{
                submitBtn.removeAttribute("disabled");
                usernameField.classList.remove("is-invalid");
                feedbackField.style.display = "none";
            }
        });
    }
});