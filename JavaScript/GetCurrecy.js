const api_url = "https://www.floatrates.com/daily/sek.json";
            async function getCurrency() {
              const response = await fetch(api_url);
              const data = await response.json();
              for (var country in data) {
                var x = document.getElementById("mySelect");
                var option = document.createElement("option");
                option.text = data[country].name;
                x.add(option);
              }
            }

            getCurrency();

            async function selectedCurrency() {
              const response = await fetch(api_url);
              const data = await response.json();
              var currency = document.getElementById("mySelect").value;
              for (var country in data) {
                if (data[country].name === currency) {
                  document.getElementById("iHaveValue").value =
                    data[country].inverseRate;
                  break;
                }
              }
            }