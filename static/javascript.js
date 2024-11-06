// Startverdier for spillet
let maxBossHealth = 10;
let bossHealth = maxBossHealth;
let damage = 2;
let defeats = 0;
let gold = 0;
let upgradeCost = 10;
let goldnum = 5;
let upgradeCost1 = 15;
let upgradeCost3 = 50;
let upgradeCost4 = 1;
let upgradeCost5 = 15
let Turret = 0;
let turetdamage = 0;
let turretskade = 5;
let kjaphet = 1000
// Referanser til HTML-elementer
const bossButton = document.getElementById("boss");
const bossHealthDisplay = document.getElementById("bossHealth");
const damageDisplay = document.getElementById("damage");
const defeatsDisplay = document.getElementById("defeats");
const goldDisplay = document.getElementById("gold");
const Turretdisplay = document.getElementById("Turret");
const Turretskadedisplay = document.getElementById("Turretskade");
const Turretskadeendisplay = document.getElementById("Turretskadeen");
const Turretspeeddisplay = document.getElementById("Turretspeed")
const upgradeButton = document.getElementById("upgradeButton");
const upgradeButton2 = document.getElementById("upgradeButton2");
const upgradeButton3 = document.getElementById("upgradeButton3");
const upgradeButton4 = document.getElementById("upgradeButton4");
const upgradeButton5 = document.getElementById("upgradeButton5")

// Oppdater HTML-elementene basert på startverdier
bossHealthDisplay.textContent = bossHealth;
damageDisplay.textContent = damage;
defeatsDisplay.textContent = defeats;
goldDisplay.textContent = gold;
Turretdisplay.textContent = Turret;
Turretskadedisplay.textContent = turetdamage;
Turretskadeendisplay.textContent = turretskade;
Turretspeeddisplay.textContent = kjaphet;


function bossdead(){
    if (bossHealth <= 0) {
        defeats++;
        gold += goldnum;
        maxBossHealth += 5;
        bossHealth = maxBossHealth;
        defeatsDisplay.textContent = defeats;
        goldDisplay.textContent = gold;
        bossHealthDisplay.textContent = bossHealth; 
        
        // Send defeats til serveren
        fetch('/update_defeats', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ defeats: defeats }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log("Defeats updated successfully. New value:", data.new_defeats);
            } else {
                console.error("Failed to update defeats:", data.error);
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function updatte(){
    bossHealthDisplay.textContent = bossHealth;
}
setInterval(updatte, 1)

// Funksjon for hva som skjer når man klikker på bossen
bossButton.addEventListener("click", () => {
    bossHealth -= damage; // Bossen tar skade
    bossHealth = Math.max(0, bossHealth);

    // Oppdaterer bossens liv i visningen
    bossHealthDisplay.textContent = bossHealth;
    if (bossHealth === 0) {
        bossdead();
    }
});

function Turetsgreie(){
    if (bossHealth >= 0){
        turetdamage = Turret * turretskade;
        bossHealth -= turetdamage; // Tårnene skader bossen
        bossHealth = Math.max(0, bossHealth);
        bossHealthDisplay.textContent = bossHealth; 
        Turretskadedisplay.textContent = turetdamage;
        
        if (bossHealth === 0) {
            bossdead();
        }
        
    }
}
// Funksjon for å kjøpe oppgraderinger
upgradeButton.addEventListener("click", () => {
    if (gold >= upgradeCost) {
        gold -= upgradeCost; // Trekk kostnaden fra gull
        damage *= 2; // Øker skade per klikk
        upgradeCost *= 2; // Øker kostnaden for neste oppgradering

        // Oppdater HTML-elementene
        damageDisplay.textContent = damage;
        goldDisplay.textContent = gold;
        upgradeButton.textContent = `Dobler damage (Koster ${upgradeCost} Gull)`;
    } else {
        upgradeButton.textContent = `Du har ikke nok gull til å kjøpe oppgraderingen!(Koster ${upgradeCost} Gull)`;
    
    }
});
//gold uppgrade
upgradeButton2.addEventListener("click", () => {
    if (gold >= upgradeCost1) {
        gold -= upgradeCost1; // Trekk kostnaden fra gull
        goldnum += 5; // Øker skade per klikk
        upgradeCost1 += 10; // Øker kostnaden for neste oppgradering

        // Oppdater HTML-elementene
        damageDisplay.textContent = damage;
        goldDisplay.textContent = gold;
        upgradeButton2.textContent = `5 mer gull per greie (Koster ${upgradeCost1} Gull)`;
    } else {
        upgradeButton2.textContent = `Du har ikke nok gull til å kjøpe oppgraderingen!(Koster ${upgradeCost1} Gull)`;
    
    }
});
//  turrets uppgrade
upgradeButton3.addEventListener("click", () => {
    if (gold >= upgradeCost3) {
        gold -= upgradeCost3; // Trekk kostnaden fra gull
        Turret += 1; 
        upgradeCost3 += 50; // Øker kostnaden for neste oppgradering

        // Oppdater HTML-elementene
        Turretdisplay.textContent = Turret;
        Turretskadedisplay.textContent = turetdamage;
        Turretskadeendisplay.textContent = turretskade;
        goldDisplay.textContent = gold;
        upgradeButton3.textContent = `Tårn som gjør automatisk skade (Koster ${upgradeCost3} Gull)`;
    } else {
        upgradeButton3.textContent = `Du har ikke nok gull til å kjøpe oppgraderingen!(Koster ${upgradeCost3} Gull)`;
    
    }
});
// nytt greie
upgradeButton4.addEventListener("click", () => {
    if (gold >= upgradeCost4) {
        gold -= upgradeCost4; // Trekk kostnaden fra gull
        turretskade += 0.5; // Øker skade per klikk
        upgradeCost4 += 5; // Øker kostnaden for neste oppgradering

        // Oppdater HTML-elementene
        Turretdisplay.textContent = Turret;
        Turretskadedisplay.textContent = turetdamage;
        Turretskadeendisplay.textContent = turretskade;
        goldDisplay.textContent = gold;
        upgradeButton4.textContent = `Turret skade (Koster ${upgradeCost4} Gull)`;
    } else {
        upgradeButton4.textContent = `Du har ikke nok gull til å kjøpe oppgraderingen!(Koster ${upgradeCost4} Gull)`;
    
    }
});
upgradeButton5.addEventListener("click", () => {
    if (gold >= upgradeCost5 && kjaphet >= 100) {
        gold -= upgradeCost5; // Trekk kostnaden fra gull
        kjaphet -= 10; // Øker skade per klikk
        upgradeCost5 += 5; // Øker kostnaden for neste oppgradering
        
        if (intervalId) {
            clearInterval(intervalId);
        }
        intervalId = setInterval(Turetsgreie, kjaphet);

        // Oppdater HTML-elementene
        Turretdisplay.textContent = Turret;
        Turretskadedisplay.textContent = turetdamage;
        Turretskadeendisplay.textContent = turretskade;
        Turretspeeddisplay.textContent = kjaphet;
        goldDisplay.textContent = gold;
        upgradeButton5.textContent = `Kjappere skyting av turrets (Koster ${upgradeCost5} Gull)`;
}   
    else if (kjaphet <= 100){
        upgradeButton5.textContent = `Maks hastighet på turret skudd`; 
        
    } 
    else {
        upgradeButton5.textContent = `Du har ikke nok gull til å kjøpe oppgraderingen!(Koster ${upgradeCost5} Gull)`;
    }
    
});



intervalId = setInterval(Turetsgreie, kjaphet);