async function analyze() {
  const url = document.getElementById("urlInput").value;
  const output = document.getElementById("output");
  output.style.display = "block";
  output.innerHTML = "جاري التحليل...";

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: url })
    });
    const data = await response.json();

    if (data.error) {
      output.innerHTML = "❌ خطأ: " + data.error;
    } else {
      output.innerHTML = `
        <strong>العنوان:</strong> ${data.title}<br>
        <strong>السعر:</strong> ${data.price}<br>
        <strong>المساحة:</strong> ${data.area} م²<br>
        <strong>سعر المتر:</strong> ${data.price_per_m2} <br>
        <strong>التقييم:</strong> ${data.evaluation}
      `;
    }
  } catch (err) {
    output.innerHTML = "حدث خطأ أثناء التحليل.";
  }
}
