// Small progressive enhancement: announce a selected resume file in the upload card.
document.addEventListener('change', function (event) {
  const input = event.target;
  if (input && input.matches('.upload-zone input[type="file"]') && input.files && input.files[0]) {
    const label = input.closest('.upload-zone').querySelector('b');
    if (label) label.textContent = input.files[0].name;
  }
});
