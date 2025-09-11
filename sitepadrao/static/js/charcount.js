document.addEventListener("DOMContentLoaded", function () {
    console.log("DOMContentLoaded");
    document.querySelectorAll(".charcount-wrapper").forEach(function (wrapper) {
        const textarea = wrapper.querySelector("textarea");
        const counter = wrapper.querySelector(".count");
        const maxLength = wrapper.querySelector(".charcount-display")?.dataset.maxlength;

        function updateCount() {
            const length = textarea.value.length;
            counter.textContent = length;
            console.log(length);
            if (maxLength) {
                if (length >= maxLength) {
                    counter.style.color = "red";
                } else if (length > maxLength * 0.8) {
                    counter.style.color = "orange";
                } else {
                    counter.style.color = "inherit";
                }
            }
        }

        textarea.addEventListener("input", updateCount);
        updateCount();
    });
});
