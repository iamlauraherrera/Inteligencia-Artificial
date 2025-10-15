"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  Cadenas de Markov / N-gramas (simple, sin libs)            ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Autor: Laura Herrera                                                         ║
║ Fecha: 2025-10-14                                                            ║
║ Descripción:                                                                 ║
║  - Unigrama, Bigrama (como casos simples de n-gramas)                        ║
║  - Cadena de Markov de orden k (k≥1) con <START>/<END>                       ║
║  - Entrenamiento sobre un corpus, generación y consulta de distribuciones    ║
║  - Sin librerías externas (solo re, random, collections)                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations
import re
import random
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Iterable, Optional

# -----------------------------------------------------------------------------
# Utilidades
# -----------------------------------------------------------------------------
def extraer_palabras(texto: str) -> List[str]:
    """Extrae palabras [a-zA-Z]+ en minúsculas del texto."""
    return re.findall(r"\b[a-zA-Z]+\b", (texto or "").lower())

def tok_start(k: int) -> Tuple[str, ...]:
    return tuple(["<START>"] * k)

# -----------------------------------------------------------------------------
# Corpus base (puedes editarlo/expandirlo desde la UI)
# -----------------------------------------------------------------------------
ai_corpus = """
EL CRIMEN Y EL CASTIGO




PRIMERA PARTE




I

Una tarde muy calurosa de principios de julio, salió del cuartito que
ocupaba, junto al techo de una gran casa de cinco pisos, un joven, que,
lentamente y con aire irresoluto, se dirigió hacia el puente de K***.

Tuvo suerte, al bajar la escalera, de no encontrarse a su patrona
que habitaba en el piso cuarto, y cuya cocina, que tenía la puerta
constantemente sin cerrar, daba a la escalera. Cuando salía el joven,
había de pasar forzosamente bajo el fuego del enemigo, y cada vez que
esto ocurría experimentaba aquél una molesta sensación de temor que,
humillándole, le hacía fruncir el entrecejo. Tenía una deuda no pequeña
con su patrona y le daba vergüenza el encontrarla.

No quiere esto decir que la desgracia le intimidase o abatiese; nada
de eso; pero la verdad era que, desde hacía algún tiempo, se hallaba
en cierto estado de irritación nerviosa, rayano con la hipocondría.
A fuerza de aislarse y de encerrarse en sí mismo, acabó por huir, no
solamente de su patrona, sino de toda relación con sus semejantes.

La pobreza le aniquilaba y, sin embargo, dejó de ser sensible a sus
efectos. Había renunciado completamente a sus ocupaciones cotidianas y,
en el fondo, se burlaba de su patrona y de las medidas que ésta pudiera
tomar en contra suya. Pero el verse detenido por ella en la escalera,
el oír las tonterías que pudiera dirigirle, el sufrir reclamaciones,
amenazas, lamentos y verse obligado a responder con pretextos y
mentiras, eran para él cosas insoportables. No; era preferible no ser
visto de nadie, y deslizarse como un felino por la escalera.

Esta vez él mismo se asombró, cuando estuvo en la calle, del temor de
encontrar a su acreedora.

«¿Debo asustarme de semejantes simplezas cuando proyecto un golpe tan
atrevido?--se decía, riendo de un modo extraño--. Sí... el hombre lo
tiene todo entre las manos y lo deja que se le escape en sus propias
narices tan sólo a causa de su holgazanería... Es un axioma... Me
gustaría saber qué es lo que le da más miedo a la gente... Creo que
temen, sobre todo, lo que les saca de sus costumbres habituales... Pero
hablo demasiado... Tal vez por el hábito adquirido de monologar con
exceso no hago nada... Verdad es que con la misma razón podría decir
que es a causa de no hacer nada por lo que hablo tanto. Un mes completo
hace que he tomado la costumbre de monologar acurrucado durante días
enteros en un rincón, con el espíritu ocupado con mil quimeras. Veamos:
¿por qué me doy esta carrera? ¿Soy capaz de _eso_? ¿Es serio _eso_?
No, de ningún modo; patrañas que entretienen mi imaginación, puras
fantasías.»

Hacía en la calle un calor sofocante. La multitud, la vista de la cal,
de los ladrillos, de los andamios y esta fetidez especial, tan conocida
de los habitantes de San Petersburgo que no pueden alquilar una casa
de campo durante el verano, todo contribuía a irritar cada vez más los
nervios del joven. El insoportable olor de las tabernas y figones, muy
numerosos en aquellas partes de la ciudad, y los borrachos que a cada
paso se encontraba, aunque aquel era día laborable, acabaron por dar al
cuadro un repugnante colorido.

Hubo un momento en que los finos rasgos de la fisonomía de nuestro
héroe expresaron amargo disgusto. Digamos con este motivo que no
carecía de ventajas físicas; era alto, enjuto y bien formado; tenía el
cabello castaño y hermosos ojos de color azul obscuro. Poco después
cayó en profunda abstracción o más bien en una especie de sopor
intelectual. Andaba sin reparar en los objetos que encontraba al paso
y sin querer reparar en ellos. De vez en cuando murmuraba algunas
palabras; porque, como él reconocía poco antes, tenía por costumbre el
monologar. En aquel momento echó de ver que se embrollaban sus ideas, y
que estaba muy débil: puede decirse que había pasado dos días sin comer.

Iba tan miserablemente vestido, que otro que no hubiera sido él habría
tenido escrúpulos para salir en pleno día con semejantes andrajos. A
decir verdad, en aquel barrio se podía ir de cualquier modo. En los
alrededores del Mercado del Heno, en esas calles del centro de San
Petersburgo habitadas en su mayoría por obreros, a nadie asombra la más
rara indumentaria. Pero tan arrogante desdén existía en el alma del
joven, que, a pesar de su vergüenza, algunas veces cándida, no le daba
ninguna de ostentar en la calle sus harapos.

Otra cosa hubiera sido de tropezar alguno de sus amigos o antiguos
camaradas, de cuyo encuentro huía siempre... Sin embargo, se detuvo de
pronto al notar, merced a esas palabras pronunciadas con voz burlona,
que atraía la atención de los paseantes: «¡Ah, eh! un sombrero alemán».
El que acababa de lanzar esta exclamación era un borracho a quien
conducían, no sabemos dónde ni por qué, en una gran carreta.

Con un movimiento convulsivo, el aludido se quitó el sombrero y se
puso a examinarlo. Era el tal sombrero de copa alta, comprado en casa
de Zimmerman, pero ya muy estropeado, raído, agujereado, cubierto de
abolladuras y de manchas, sin alas: en una palabra, horrible. A pesar
de todo, lejos de mostrarse herido en su amor propio, el poseedor de
aquella especie de gorro experimentó más inquietud que humillación.

--¡Ya me lo figuraba yo!--murmuró en su turbación--; ¡lo había
presentido! Pero lo peor es que en una miseria como la mía, una
tontería insignificante puede echar a perder el negocio. Sí; este
sombrero produce demasiado efecto, y el efecto nace precisamente de
que es ridículo. Para llevar estos harapos es indispensable usar
gorra. Mejor que este mamarracho será una boina vieja. No hay quien
lleve semejantes sombreros; de seguro que éste llama la atención a una
versta[1] de distancia. Después lo recordarían y podría ser un indicio;
lo importante es no llamar la atención de nadie... Las cosas pequeñas
tienen siempre importancia; por ellas suele ser por las que uno se
pierde.

       [1] Es la milla rusa, que equivale poco más o menos a un
       kilómetro.

No tenía que ir muy lejos; sabía la distancia exacta que separaba su
casa del sitio adonde se dirigía; setecientos pasos justos. Los había
contado cuando su proyecto no era más que un vago sueño. En aquella
época no creía que llegase el día en que se trocara lo imaginado en
acción; se limitaba a acariciar en su mente una idea espantosa y
seductora a la vez; pero desde aquel tiempo, un mes hacía, comenzaba
a considerar las cosas de otro modo. Aunque en todos sus soliloquios
se reprochase su falta de energía y su irresolución, habíase ido, sin
embargo, habituando poco a poco e involuntariamente, en cierto modo, a
mirar como posible la realización de su sueño, no obstante continuar
dudando de sí mismo. En aquel momento iba a hacer el _ensayo general_
de su empresa, y a cada paso aumentaba su agitación.

Con el corazón desfallecido y el cuerpo agitado por nervioso temblor,
se aproximó a una inmensa casa que daba de un lado al canal y del
otro a la calle... Este edificio, dividido en multitud de cuartitos
de alquiler, tenía por inquilinos industriales de todas las clases,
sastres, cerrajeros, cocineras, alemanes de diferentes categorías,
mujeres públicas y humildes empleados, etc. Un continuo hormiguero
entraba y salía por las dos puertas. Tres o cuatro _dvorniks_[2]
prestaban sus servicios en esta casa. Con gran satisfacción suya, el
joven no encontró a nadie. Después de haber pasado el umbral sin ser
notado, tomó por la escalera de la derecha.

       [2] Porteros.

Conocía ya esta escalera angosta y tenebrosa cuya obscuridad no le
desagradaba, pues así no eran de temer las miradas curiosas. «Si ahora
tiemblo, ¿qué será cuando venga en serio?», no pudo menos de pensar
cuando llegaba al cuarto piso. Allí le cerraron el paso antiguos
soldados convertidos en mozos de cuerda; mudaban los muebles de uno de
los cuartos, ocupado, el joven lo sabía, por un funcionario alemán y su
familia.

--Gracias a la marcha del alemán, no habrá durante algún tiempo en ese
rellano otro inquilino que la vieja. Esto es bueno saberlo... por lo
que pueda suceder.

Así pensó, y tiró del llamador de la casa de la vieja. Débilmente sonó
la campanilla, como si fuese de hojalata y no de cobre. Tales son en
esas casas las campanillas de todos los pisos.

Sin duda había olvidado este detalle; aquel sonido particular debió de
traerle repentinamente a la memoria algún recuerdo, porque el joven
se estremeció y se alteraron sus nervios. Al cabo de un instante se
entreabrió la puerta, y, por la estrecha abertura, la dueña de la casa
examinó al recién venido con manifiesta desconfianza; brillaban sus
ojillos como dos puntos luminosos en la obscuridad, pero al advertir
que había gente en el descansillo se tranquilizó y abrió por completo
la puerta. El joven entró en un sombrío recibimiento, dividido en dos
por un tabique, tras del cual estaba la cocina. En pie delante del
joven, la vieja callaba interrogándole con la vista. Era una mujer de
sesenta años, pequeñuela y delgada, de nariz puntiaguda y de mirada
maliciosa.

Tenía la cabeza descubierta, y los cabellos, que comenzaban a
encanecer, relucían untados de aceite. Llevaba puesto al cuello, que
era largo y delgado como la pata de una gallina, una tira de franela,
y, a pesar del calor, habíase echado sobre los hombros un abrigo
apolillado y amarillento. La vieja tosía a menudo. Debió de mirarla el
joven de un modo singular, porque los ojos de la anciana recobraron
bruscamente su expresión de desconfianza.

--Raskolnikoff, estudiante. Estuve aquí, en esta casa, hace un mes--se
apresuró a decir el joven, medio inclinándose, porque había pensado que
lo mejor era mostrarse afable.

--Sí, lo recuerdo, lo recuerdo--respondió la vieja, que no cesaba de
mirarle con recelo.

--Pues bien... Vengo otra vez por un asuntillo del mismo
género--continuó Raskolnikoff algo desconcertado y sorprendido de la
desconfianza que inspiraba.

«Quizá esta mujer ha sido siempre lo mismo; pero la otra vez no lo eché
de ver»--pensó el joven desagradablemente impresionado.

La vieja permaneció algún tiempo silenciosa como si reflexionase. Luego
señaló la puerta de la sala a su visitante, y le dijo haciéndose a un
lado para dejarle pasar delante de ella.

--Entre usted.

La salita en la cual fué introducido el joven, tenía tapizadas las
paredes de color amarillo; en las ventanas, con cortinas de muselina,
había tiestos de geranios; el sol poniente arrojaba sobre aquello
viva claridad. «¡Sin embargo, _entonces_ brillaba el sol de la misma
manera!»--dijo Raskolnikoff para su coleto y dirigió rápidamente
una mirada en torno suyo, para darse cuenta de todos los objetos y
grabarlos en la memoria. En la habitación no había nada de particular.
Los muebles, de madera amarilla, eran muy viejos: un sofá con gran
respaldo vuelto, una mesa de forma oval frente a frente del sofá, un
lavabo y un espejo entre las dos ventanas, sillas a lo largo de las
paredes, dos o tres grabados, sin valor, que representaban señoritas
alemanas con pájaros en las manos; a esto se reducía el mobiliario.

En un rincón, delante de una pequeña imagen, ardía una lámpara; tanto
los muebles como el suelo relucían de puro limpios.

«Es Isabel la que arregla todo esto»--pensó el joven.

En toda la habitación no se veía un grano de polvo.

«Es preciso venir a las casas de estas malas viejas viudas para
ver tanta limpieza»--continuó monologando Raskolnikoff, y miró con
curiosidad la cortina de indiana que ocultaba la puerta correspondiente
a otra salita; en esta última, en la que jamás había entrado, estaban
la cama y la cómoda de la vieja.

--¿Qué quiere usted?--preguntó secamente la dueña de la casa, que,
habiendo seguido a su visitante, se colocó frente a él para examinarle
de cerca.

--He venido a empeñar una cosa. Véala usted.

Y sacó del bolsillo un reloj de plata viejo y aplastado, que tenía
grabado en la tapa un globo. La cadena era de acero.

--Aun no me ha devuelto usted la cantidad que le tengo prestada;
anteayer cumplió el plazo.

--Le pagaré aún el interés del otro mes; tenga un poco de paciencia.

--Conste, amiguito, que puedo esperar, si quiero, o vender el objeto
empeñado, si se me antoja...

--¿Qué me da por este reloj, Alena Ivanovna?

--Lo que trae aquí es una miseria; esto no vale nada. La otra vez le di
a usted dos billetes pequeños por un anillo que se puede comprar nuevo
en la joyería por rublo y medio.

--Déme usted cuatro rublos y lo desempeñaré. Perteneció a mi padre.
Pronto recibiré dinero.

--Rublo y medio, y he de cobrar el interés por adelantado.

--¡Rublo y medio!--exclamó el joven.

--Acepta usted, ¿sí o no?

Y dicho esto, la mujer alargó el reloj al visitante. Este lo tomó e
iba a retirarse, irritado, cuando reflexionó que la prestamista era su
último recurso; además, había ido allí para otra cosa.

--¡Venga el dinero!--dijo con tono brutal.

La vieja buscó las llaves en el bolsillo y entró en la habitación
contigua. Cuando el joven se quedó solo en la sala, se puso a escuchar,
entregándose a diversos cálculos. A poco oyó cómo la usurera abría la
cómoda.

«Debe ser el cajón de arriba--supuso Raskolnikoff--; ahora sé que
lleva las llaves en el bolsillo derecho, y que están todas reunidas
en una anilla de acero... Una de ellas es tres veces más gruesa
que las otras, y tiene las guardas dentadas; esa llave no es de la
cómoda, seguramente. Por lo tanto, debe haber alguna caja o alguna
arca de hierro... Es curioso. Las llaves de las arcas de hierro son
generalmente de esa forma... ¡Pero qué innoble es todo esto!...»

Volvió a entrar la vieja.

--Mire usted: como cobro una grivna[3] al mes por cada rublo, y
empeña usted el reloj en rublo y medio le desquito 15 kopeks y queda
satisfecho el interés por adelantado. Además, como usted me suplica que
espere otro mes para devolverme los dos rublos que le tengo prestados,
me debe usted por este concepto 20 kopeks, que, unidos a los 15 que le
desquito, componen 35. Tengo, pues, que darle a usted un rublo y 15
kopeks. Aquí están.

       [3] Moneda de diez kopeks equivalente a cuatro céntimos de
       franco. El rublo, que vale unos cuatro francos, se divide en
       diez kopeks.

--¡Cómo! ¿De modo que no me da usted ahora más que un rublo y 15 kopeks?

--Nada más tengo que darle a usted.

Tomó el joven el dinero sin discutir. Miraba a la vieja sin darse prisa
a marcharse. Parecía tener intención de hacer algo; pero no sabía con
precisión lo que deseaba...

--Es posible, Alena Ivanovna, que venga pronto con otra cosa... Una
cigarrera... de plata... muy bonita... en cuanto me la devuelva un
amigo a quien se la he prestado.

Dijo estas palabras con manifiesto embarazo.

--Pues bien, entonces hablaremos.

--Adiós... ¿Sigue usted viviendo sola, sin que su hermana le haga
compañía?--preguntó con el tono más indiferente que le fué posible en
el momento en que entraba en la antesala.

--¿Y qué le importa a usted mi hermana?

--Es verdad, se lo preguntaba a usted por decir algo... Adiós, Alena
Ivanovna.

Raskolnikoff salió muy alterado; al bajar la escalera se detuvo muchas
veces como rendido por sus emociones.

«¡Dios mío, cómo subleva el corazón todo esto!--exclamó cuando llegó a
la calle--. ¡Es posible, es posible que yo...!

No, es una tontería, un absurdo--añadió resueltamente--. ¿Y ha podido
ocurrírseme tan espantosa idea? ¿He de ser yo capaz de tal infamia?
¡Esto es odioso, innoble, repugnante!... ¿Y por espacio de un mes
entero yo...?»

Para expresar la agitación que sentía, eran impotentes las
exclamaciones y palabras. La sensación de inmenso disgusto que comenzó
a oprimirle poco antes cuando se encaminaba a casa de la vieja,
alcanzaba ahora intensidad tan grande que el joven no sabía cómo
substraerse a semejante suplicio... Caminaba por la acera como un
borracho, sin reparar en los transeuntes y tropezándose con ellos. En
la calle siguiente volvió a recobrar ánimos y, mirando en torno suyo,
advirtió que estaba cerca de una taberna; una escalera situada al nivel
de la acera daba entrada a la cueva del establecimiento. Raskolnikoff
vió salir en aquel instante a dos borrachos que se apoyaban el uno en
el otro, injuriándose recíprocamente.

Vaciló el joven un instante, y después bajó la escalera. Nunca había
entrado en una taberna; pero en aquel momento sentía vahídos, le
atormentaba ardiente sed. Tenía ganas de beber cerveza fresca, y
atribuía su debilidad a lo vacío del estómago. Después de sentarse en
un rincón, sombrío y sucio, ante una mesita mugrienta, pidió cerveza y
bebió el primer vaso con avidez.

Al punto sintió un gran alivio y se esclarecieron sus ideas.

«Todo esto es absurdo--se dijo ya confortado--. No había motivo para
turbarse. ¡Es sencillamente efecto de un mal físico; con un vaso de
cerveza y un bizcocho habría recobrado la fuerza de mi inteligencia,
la precisión de mis ideas, el vigor de mis resoluciones! ¡Oh, qué
insignificante es todo ello!»

A pesar de tan desdeñosa conclusión, estaba contento, como si se viese
libre de un peso enorme, y dirigía miradas amistosas a las personas
presentes. Pero al mismo tiempo sospechó que fuese ficticio aquel
retorno a la energía.

Quedaba muy poca gente en la taberna; después de los dos borrachos,
salió una banda de cinco músicos, y el establecimiento quedó
silencioso; no había en él más que tres personas: un individuo algo
ebrio, cuyo exterior indicaba un hombre de la clase media, estaba
sentado delante de una botella de cerveza. Cerca de él, tendido en el
banco, dormitaba un sujeto alto y grueso, de barba blanca, vestido con
un largo levitón, y en completo estado de embriaguez.

De cuando en cuando parecía despertarse bruscamente; se ponía a hacer
sonar los dedos, apartando los brazos y moviendo rápidamente el busto,
sin levantarse del banco sobre el cual estaba echado. Tales gestos y
ademanes servían de acompañamiento a una canción necia, de la que el
hombre se esforzaba para recordar los versos:

    Durante un año entero
    yo he acariciado.
    Du-ran-te un a-ño en-te-ro
    yo he a-ca-ri-cia-do
    a mi mujer.

O esta otra:

    En la Podiatcheshaïa.
    He encontrado a mi vieja...

Nadie hacía caso de la alegría de aquel melómano. Su mismo compañero
escuchaba todos aquellos gorjeos en silencio y haciendo muecas de
disgusto. El tercer consumidor parecía un antiguo funcionario. Sentado
aparte se llevaba de vez en cuando el vaso a los labios, mirando en
derredor suyo; parecía que también él era presa de cierta agitación.


II

Raskolnikoff no estaba habituado a la multitud, y, conforme hemos
dicho, desde hacía algún tiempo evitaba las compañías de sus
semejantes; pero de repente se sintió atraído hacia los hombres.
Cualquiera hubiera dicho que se operaba en él una especie de revolución
y que el instinto de sociabilidad recobraba sus derechos. Entregado
durante un mes completo a los sueños morbosos que la soledad engendra,
tan fatigado estaba nuestro héroe de su aislamiento, que deseaba
encontrarse, aunque no fuese más que un minuto, en un ambiente humano.
Así, pues, por innoble que fuese aquella taberna, se sentó ante una de
las mesas con verdadero placer.

El dueño del establecimiento estaba en otra habitación; pero salía y
entraba frecuentemente en la sala. Desde el umbral, sus hermosas botas
de altas y rojas vueltas atraían inmediatamente las miradas; llevaba un
_paddiovka_ y un chaleco de raso negro horriblemente manchado de grasa
y no tenía corbata; la cara parecía untada de aceite. Tras el mostrador
se hallaba un mozo de catorce años, y otro más joven servía a los
parroquianos. Expuestas en el aparador había varias vituallas, trozos
de cohombro, galleta negra y bacalao cortado en pedazos; todo exhalaba
olor a rancio. El calor era tan insoportable y la atmósfera estaba tan
cargada de vapores alcohólicos, que parecía imposible pasar en aquella
sala cinco minutos sin emborracharse.

Ocurre a veces que nos encontramos con desconocidos que nos interesan
por completo a primera vista, antes de cruzar una palabra con ellos.
Esto fué lo que sucedió a Raskolnikoff respecto al individuo que tenía
el aspecto de un antiguo funcionario. Más tarde, al acordarse de esta
primera impresión, el joven la atribuyó a un presentimiento. No quitaba
los ojos del desconocido, sin duda porque este último no dejaba tampoco
de mirarle, y parecía muy deseoso de trabar conversación con él. A
los demás consumidores, y aun al mismo tabernero, los miraba con aire
impertinente y altanero; eran, evidentemente, personas que estaban por
debajo de él en condición social y en educación para que se dignase
dirigirles la palabra.

Aquel hombre, que había pasado ya de los cincuenta años, era de
mediana estatura y de complexión robusta. La cabeza, en gran parte
calva, no conservaba más que algunos cabellos grises. El rostro largo,
amarillo o casi verde, denunciaba hábitos de incontinencia; bajo los
gruesos párpados brillaban unos ojillos rojizos, muy vivaces. Lo que
más impresionaba en su fisonomía era la mirada en que la llama de la
inteligencia y del entusiasmo se alternaba con no sé qué expresión de
locura. Este personaje llevaba sobretodo negro, viejo, todo desgarrado,
y no gustándole, sin duda, llevarle abierto, lo abrochaba correctamente
con el único botón que el sobretodo tenía. El chaleco, de _nanquin_,
dejaba ver la pechera de la camisa rota y llena de manchas. La ausencia
de barba denunciaba en él al funcionario; pero debía haberse afeitado
en una época bastante remota, porque le azuleaban las mejillas con un
pelo muy espeso. Notábase en sus maneras cierta gravedad burocrática;
pero, en aquel momento, parecía conmovido. Se revolvía los cabellos,
y, de tiempo en tiempo, apoyaba los codos en la mesa pringosa, sin
temor a mancharse las mangas agujereadas, y reclinaba la cabeza en las
dos manos. Por último, comenzó a decir en voz alta y firme, mirando a
Raskolnikoff.

--¿Será una indiscreción por mi parte, señor, hablar con usted?
Porque es lo cierto que, a pesar de la sencillez de su traje, mi
experiencia distingue en usted un hombre muy bien educado y no un
asiduo parroquiano de taberna. Siempre he dado mucha importancia a
la educación, unida, por supuesto, a las cualidades del corazón.
Pertenezco al _Tchin_[4]. Permítame usted que me presente: Simón
Ivanovitch Marmeladoff, consejero titular. ¿Me es lícito preguntarle si
ha pertenecido usted a la administración?

       [4] Así llaman en Rusia a todos los que pertenecen de una
       manera u otra a la administración pública y constituyen como
       una casta especial.

--No, yo soy estudiante--respondió el joven sorprendido de aquel cortés
lenguaje, y, sin embargo, molesto al ver que un desconocido le dirigía
la palabra a quema ropa.

Aunque se hallaba en su cuarto de hora de sociabilidad, sintió en aquel
momento que se le despertara el mal humor que solía experimentar cuando
un extraño trataba de ponerse en relaciones con él.

--¿De modo que es usted estudiante, o lo sigue siendo?--repuso
vivamente el funcionario--; es precisamente lo que yo pensaba. ¡Tengo
olfato, señor, un olfato muy fino, gracias a mi larga experiencia!

Se llevó el dedo a la frente, indicando con este gesto la opinión que
tenía de su capacidad cerebral.

--Pero, dispénseme... ¿no ha terminado usted realmente sus estudios?

Se levantó, tomó su vaso y fué a sentarse al lado del joven. A pesar de
estar ebrio, hablaba distintamente y sin gran incoherencia. Al verle
arrojarse sobre Raskolnikoff como sobre una presa, se hubiera podido
suponer que él también, desde hacía un mes, no había despegado los
labios ni para decir esta boca es mía.

--Señor--declaró con cierta solemnidad--, la pobreza no es un vicio,
seguramente, de la misma manera que la embriaguez no es una virtud.
Pero la indigencia, señor, la indigencia es un vicio de los peores. En
la pobreza conserva uno el orgullo nativo de sus sentimientos; en la
indigencia no se conserva nada, ni siquiera se le echa a uno a palos
de la sociedad humana, sino a escobazos, que son más humillantes. Y
hacen bien, porque el indigente está dispuesto a envilecerse y esto es
lo que explica la taberna. Señor, hace un mes que Lebeziatnikoff pegó
a mi mujer. Y dígame, ¿pegar a mi mujer no es herirme a mí en el punto
más sensible? ¿Me comprende usted? Permítame que le haga otra pregunta,
¡oh! por simple curiosidad: ¿Ha pasado usted alguna noche en el Neva en
los barcos de heno?

--No, jamás--contestó Raskolnikoff--; ¿por qué me lo pregunta usted?

--Pues bien, para mí será hoy la quinta vez que dormiré allí.

Llenó el vaso, lo apuró y se quedó pensativo. En efecto, en su traje
y en sus cabellos se veían algunas briznas de heno. A juzgar por las
apariencias, lo menos hacía cinco días que no se había desnudado ni
lavado la cara. Sus gruesas y rojas manos, con las uñas de luto,
estaban también extremadamente sucias.

La sala entera le escuchaba, aunque, a decir verdad, con bastante
despreocupación. Los mozos se reían detrás del mostrador. El tabernero
había bajado también, sin duda para oír a aquel hombre original.
Sentado a cierta distancia bostezaba con aire importante. Evidentemente
Marmeladoff era conocido desde hacía algún tiempo en la casa. Según
todas las probabilidades, debía su notoriedad a la costumbre de hablar
en la taberna con todos los parroquianos que se ponían a su alcance.
Tal costumbre se convierte en una necesidad para ciertos borrachos,
principalmente para aquellos que son tratados con dureza por esposas
poco tolerantes; tratan de adquirir en la taberna con sus compañeros de
orgía la consideración que no encuentran en sus hogares.

--¡Por vida de...!--dijo en voz fuerte el tabernero--. ¿Por qué no
trabajas, por qué no vas a la oficina, puesto que eres empleado?

--¿Por qué no trabajo, señor?--siguió diciendo Marmeladoff, encarándose
exclusivamente con Raskolnikoff, como si éste le hubiera dirigido la
pregunta--. ¿Por qué no trabajo? ¿Cree usted que mi inutilidad no me
disgusta? Cuando, hace un mes, Lebeziatnikoff maltrató a mi mujer con
sus propias manos, mientras yo asistía, ebrio y medio muerto, a tal
escena, ¿cree usted que yo no sufría? Permítame usted, joven; ¿le ha
ocurrido a usted... ¡hum!... le ha ocurrido solicitar un préstamo sin
esperanza?

--Sí... Es decir, ¿qué entiende usted por eso de sin esperanza?

--Quiero decir, sabiendo perfectamente de antemano que no le darán a
usted nada. Por ejemplo, usted tiene la certidumbre de que tal hombre,
tal ciudadano bien intencionado, no le prestaría un kopek; porque,
dígame usted, ¿a qué santo había de prestárselo, sabiendo que usted no
ha de devolvérselo? ¿Por piedad? Ese Lebeziatnikoff es partidario de
las nuevas ideas y aseguraba el otro día que la compasión, en nuestra
época, está prohibida hasta por la ciencia, y que tal es la doctrina
reinante en Inglaterra, en donde florece la economía política. ¿Cómo,
repito, ese hombre habrá de prestarle a usted dinero? Está usted seguro
de que no se lo prestará, y, sin embargo, se dirige usted a...

--¿Para qué ir en ese caso?--interrumpió Raskolnikoff.

--Pues porque es preciso ir a alguna parte; porque no hay otra salida
y llega un tiempo en que el hombre se decide, de buena o mala gana,
a tomar cualquier senda. Cuando mi hija única se fué a inscribir
en la policía tuve que ir también con ella (porque mi hija tiene
cartilla)--añadió entre paréntesis, mirando al joven con expresión de
inquietud--. Le advierto a usted que esto me tiene sin cuidado--se
apresuró a decir con aparente flema, en tanto que los mozos, detrás del
mostrador, y hasta el mismo tabernero sonreían--. ¡Poco me importa!
No me inquietan los movimientos de cabeza, porque estas cosas son
conocidas de todo el mundo y no hay secreto que no se descubra; no es
con desprecio sino con resignación, como yo acepto mi suerte. ¡Sea!
_¡Ecce Homo!_ Permítame, joven, que le pregunte si puede usted, o,
mejor dicho, si se atrevería usted, fijando los ojos en mí, a afirmar
que no soy un cerdo.

El joven no respondió.

El orador esperó con aire digno a que terminasen las risas provocadas
por sus últimas palabras. Después añadió:

--Es verdad; yo soy un cerdo; pero ella es una señora. ¡Llevo impreso
el sello de la bestia! Pero Catalina Ivanovna, mi esposa, es una
persona bien educada, hija de un oficial superior. Concedo que soy un
bufón empedernido; pero mi mujer tiene un gran corazón, sentimientos
elevados, instrucción... y, sin embargo... ¡Oh! ¡Si tuviese piedad de
mí! ¡Señores, señores, todos los hombres tienen necesidad de encontrar
piedad en alguna parte! Pero Catalina Ivanovna, a pesar de su grandeza
de alma, es injusta... Pues bien, con tal de que yo llegue a comprender
que cuando me tira de los cabellos, lo hace, en rigor, por interés
hacia mí... (No me avergüenzo de confesarlo: me tira de los cabellos,
joven)--insistió, creciendo en dignidad al oír nuevas carcajadas--.
Sin embargo, Dios mío, aunque no fuese más que una vez... pero no, no;
dejemos esto; es inútil hablar de ello... Ni una sola vez he obtenido
lo que deseaba; ni una sola vez se ha tenido compasión de mí... pero
tal es mi carácter; soy un verdadero bruto...

--Lo creo--dijo bostezando el tabernero.

Marmeladoff dió un puñetazo en la mesa.

--Tal es mi carácter; ¿querrá usted creer, querrá usted creer, señor,
que me he bebido hasta sus medias? No digo sus zapatos, porque esto
se comprendería, hasta cierto punto; pero son sus medias, sus medias,
las que yo me he bebido. ¡Sus medias! me he bebido también su pañoleta
de pelo de cabra, un regalo que le habían hecho; un objeto que poseía
antes de casarse conmigo y que era de su propiedad y no de la mía.
Habitamos en un cuarto muy frío; este invierno mi mujer ha pescado un
catarro y tose y escupe sangre. Tenemos tres hijos pequeños, y Catalina
Ivanovna trabaja de la noche a la mañana. Hace colada y limpia la casa,
porque desde muy joven está acostumbrada a la limpieza. Por desgracia,
tiene el pecho delicado, cierta predisposición a la tisis que me
preocupa. ¿No lo siento, por ventura? Cuando más bebo, más lo siento.
Es para sentir y sufrir más por lo que me entrego a la bebida; ¡bebo
porque quiero sufrir doblemente!

E inclinó la cabeza sobre la mesa con aire de desesperación.

--Joven--continuó en seguida incorporándose--, me parece leer en su
semblante cierto disgusto. Desde que entró usted me ha parecido
advertirlo, y por eso le he dirigido inmediatamente la palabra. Si le
cuento la historia de mi vida no es para ofrecerme a la burla de esos
ociosos, que, por otra parte, están enterados de todo, no; es porque
busco la simpatía de un hombre bien educado. Sepa usted, pues, que
mi mujer ha sido educada en una pensión aristocrática de provincia,
y que a su salida del establecimiento bailó en chal delante del
gobernador y de los otros personajes oficiales; tan contenta estaba
por haber obtenido una medalla de oro y un diploma. La medalla... la
hemos vendido hace ya mucho tiempo, ¡hum!... En cuanto al diploma, lo
conserva mi esposa en un cofre y últimamente aun lo mostraba al ama
de nuestra casa. Aunque esté a matar con ella, a mi mujer le gusta
ostentar ante los ojos de cualquiera sus éxitos pasados. No se lo echo
en cara, porque su única alegría ahora es acordarse de los hermosos
días de otro tiempo. ¡Todo lo demás se ha desvanecido! Sí, sí; tiene un
alma ardiente, orgullosa, intratable. Ella friega el suelo, come pan
negro; pero no permite que se le escatimen ciertas consideraciones. Así
es, que no ha tolerado la grosería de Lebeziatnikoff, y cuando, para
vengarse de haber sido despedido, este último le puso la mano encima,
mi mujer tuvo que guardar cama, sintiendo más el insulto hecho a su
dignidad que el dolor de los golpes recibidos.

»Cuando me casé con ella era viuda, con tres niños pequeños. Había
estado casada en primeras nupcias con un oficial de infantería, con
quien huyó de casa de sus padres; amaba extremadamente a su marido;
pero éste se dió al juego, tuvo que entendérselas con la justicia, y
murió. En los últimos tiempos pegaba a su mujer. Sé de buena tinta
que no era cariñosa con él, lo que no le impide ahora llorar por el
difunto y establecer continuamente comparaciones entre él y mi persona,
comparaciones poco lisonjeras para mi amor propio. Pero no me quejo;
más bien me complace que se imagine haber sido feliz en otro tiempo.

»Después de la muerte de su marido se encontró sola con tres hijos
pequeños, en un distrito lejano y salvaje, donde la encontré yo. Su
miseria era tal, que yo, que de eso he visto tanto, no me siento con
fuerzas para describirla. Todos sus parientes la habían abandonado; por
otra parte, su orgullo le hubiera impedido siempre implorar la piedad
de aquellas personas. Entonces, señor, entonces, yo, que era viudo
también, y que tenía de mi matrimonio una hija de catorce años, ofrecí
mi mano a aquella pobre mujer; tanta pena me daba verla sufrir.

»Instruída, bien educada, de buena familia, consintió, sin embargo,
en casarse conmigo. Esto puede dar a usted una idea de la miseria en
que la pobre viviría. Acogió mi proposición llorando, sollozando y
retorciéndose las manos, pero la acogió, porque no tenía dónde ir.

»¿Comprende usted, comprende usted lo que significan estas palabras:
«No tener ya adónde ir»? ¡Usted no lo comprende todavía!

»Durante un año entero cumplí mi deber honrada y santamente, y sin
probar una gota de esto (señaló con el dedo la media botella que tenía
delante); porque no carezco de sentimientos. Pero nada adelanté. A
poco perdía mi empleo y no por falta mía; reformas administrativas
determinaban la supresión del que desempeñaba, y entonces fué cuando
me di a la bebida... Ahora ocupamos una habitación en casa de Amalia
Ludvigovna Lippevechzel; pero ignoro con qué le pagamos y de qué
vivimos. Hay allí muchos inquilinos además de nosotros; es una ratonera
aquella casa... ¡hum!... Sí... Durante este tiempo, creció la hija que
yo tenía de mi primera mujer. No quiero hablar de lo que su madrastra
la ha hecho sufrir.

»Aunque de sentimientos nobilísimos, Catalina Ivanovna es una mujer
irascible e incapaz de contenerse en los arrebatos de su cólera... Sí,
¡vamos, es inútil hablar de esto! Como puede usted comprender, Sonia no
ha recibido una gran instrucción. Hace cuatro años traté de enseñarle
Geografía e Historia Universal; pero como yo no he estado nunca fuerte
en estas materias, y como además no tenía a mi disposición un buen
manual, no hizo grandes progresos en sus estudios: nos detuvimos en
Ciro, rey de Persia. Más tarde, cuando llegó a la edad adulta, leyó
algunas novelas. Lebeziatnikoff le prestó hace poco la _Fisiología
de Ludwig_. ¿Conoce usted esa obra? Mi hija la ha encontrado muy
interesante y aun nos ha leído muchos pasajes en alta voz. A eso se
limita toda su cultura.

»Ahora, señor, apelo a su sinceridad. ¿Cree usted en conciencia que una
joven pobre, pero honrada, pueda vivir de su trabajo? Como no tenga una
habilidad especial, ganará 15 kopeks al día, y para llegar a esa cifra
tendrá necesidad de no perder un solo minuto. ¡Pero qué digo! Sonia
hizo media docena de camisas de holanda, para el consejero de Estado
Ivan Ivanovitch Klopstok; usted habrá oído hablar de él; pues bien, no
sólo está esperando aún que se le paguen, sino que la pusieron a la
puerta llenándola de injurias, so pretexto de que no había tomado bien
la medida del cuello.

»En tanto los niños se mueren de hambre, Catalina Ivanovna se
pasea por la habitación retorciéndose las manos, mientras en sus
mejillas aparecen las manchas rojizas, propias de su enfermedad.
«Holgazana--decía a mi hija--, ¿no te da vergüenza de vivir sin hacer
nada? Bebes, comes, tienes lumbre.» Y yo pregunto ahora: ¿Qué es lo que
la pobre muchacha podría beber y comer cuando en tres días los niños no
habían visto siquiera un mendrugo de pan? Yo estaba en aquel momento
acostado... Vamos, hay que decirlo todo, borracho; pero oí que mi Sonia
respondía tímidamente con su voz dulce (la pobrecita es rubia, con una
carita siempre pálida y resignada): «Pero, Catalina Ivanovna, ¿por qué
me dice usted esas cosas?»

»Tengo que añadir que ya por tres veces Daría Frantzovna, una mala
mujer muy conocida de la policía, le había hecho insinuaciones en
nombre del propietario de la casa. «Vaya--dijo irónicamente Catalina
Ivanovna--, vaya un tesoro para guardarlo con tanto cuidado.» Pero no
la acuse usted. No tenía conciencia de lo que decía; estaba agitada,
enferma, veía llorar a sus hijos hambrientos, y lo que decía era más
bien para molestar a Sonia que para excitarla a que se entregara al
vicio... Catalina Ivanovna es así; cuando oye llorar a sus hijos les
pega, aunque sabe que lloran de hambre. Eran entonces las cinco y oí
que Sonia se levantaba, se ponía el chal y salía del cuarto.

»A las ocho volvió. Al llegar, se fué derecha a Catalina Ivanovna,
y, silenciosamente, sin proferir palabra, depositó treinta rublos de
plata delante de mi mujer. Hecho eso, tomó nuestro gran pañuelo verde
(un pañuelo que sirve para toda la familia), se envolvió la cabeza
y se echó en la cama con la cara vuelta hacia la pared; un continuo
temblor agitaba sus hombros y su cuerpo... yo continuaba en el mismo
estado... En aquel momento, joven, vi a Catalina Ivanovna que, también
silenciosamente, se arrodillaba junto al lecho de Sonia.

»Pasó toda la noche de rodillas, besando los pies de mi hija y
rehusando levantarse. Después, las dos se durmieron juntas en los
brazos una de la otra... ¡las dos!... ¡las dos!... sí; y yo continuaba
lo mismo, sumido en la embriaguez.

Se calló Marmeladoff, como si la voz le hubiera faltado; luego llenó la
copa, la vació y siguió, después de un corto silencio:

--Desde entonces, señor, a consecuencia de una circunstancia
desgraciada, y con motivo de cierta denuncia de personas perversas
(Daría Frantzovna tuvo parte principal en este negocio porque quería
vengarse de una supuesta falta de respeto), desde entonces mi hija
Sonia[5] Semenovna fué inscrita en el registro de policía y se vió
obligada a dejarnos. Amalia Ludvigovna se ha mostrado inflexible en
este punto, sin tener en cuenta que ella misma, en cierto modo, había
favorecido las intrigas de Daría Frantzovna.

       [5] Sonia es la fórmula familiar de Sofía, y Sonetchka
       diminuto cariñoso del mismo nombre.

»Lebeziatnikoff se ha unido a ella... ¡hum! y con motivo de lo de Sonia
fué la cuestión que Catalina Ivanovna tuvo con él. En un principio
estuvo muy solícito con Sonetchka; pero de repente se sintió herido
en su amor propio. «¿Cómo un hombre de corazón--dijo--ha de habitar
en la misma casa que semejante desdichada?» Catalina Ivanovna tomó
partido por Sonia, y la disputa acabó en golpes... En la actualidad
mi hija viene a menudo a vernos a la caída de la tarde, y ayuda con
lo que puede a mi mujer. Vive en casa de Kapernumoff, un sastre cojo
y tartamudo. Sus hijos, que son varios, tartamudean como él, y hasta
su mujer tiene no sé qué defecto en la lengua... Todos comen y duermen
en la misma sala; pero a Sonia le han cedido una habitación, separada
de la de sus huéspedes por un tabique... ¡hum! sí... Son personas
muy pobres y tartamudas... Bueno... Una mañana me levanté, me puse
mis harapos, elevé las manos al cielo y me fuí a ver a Su Excelencia
Ivan Afanasievitch. ¿Le conoce usted? ¿No? Pues entonces no conoce a
un santo varón... Es una vela... pero una vela que arde delante del
altar del Señor. Mi historia, que Su Excelencia se dignó oír hasta el
fin, le hizo saltar las lágrimas. «Vamos, Simón Ivanovitch--me dijo--,
has defraudado una vez mis esperanzas, pero vuelvo a tomarte, bajo
mi exclusiva responsabilidad personal.» Así se expresó, añadiendo:
«Procura acordarte de lo pasado, para no reincidir, y retírate.» Besé
el polvo de sus botas, mentalmente, por supuesto, porque Su Excelencia
no hubiera permitido que se las besase de veras; es un hombre muy
penetrado de las ideas modernas y no le gustan semejantes homenajes.
¡Pero, Dios mío, cómo se me festejó cuando anuncié en casa que tenía un
destino!

De nuevo la emoción obligó a Marmeladoff a detenerse. En aquel momento
invadió la taberna un grupo de individuos ya a medios pelos. A la
puerta del establecimiento sonaba un organillo, y la voz débil de un
chiquillo cantaba la _Petite Ferme_.

La atmósfera de la sala era pesadísima. El tabernero y los mozos
se apresuraban a servir a los recién llegados. Sin reparar en este
incidente, Marmeladoff continuó su relato; el funcionario era cada vez
más expansivo a causa de los progresos de su borrachera. El recuerdo de
su reciente reposición iluminaba como un rayo de alegría su semblante.
Raskolnikoff no perdía ni una sílaba de sus palabras.

--Han transcurrido cinco semanas, señor, desde que Catalina Ivanovna
y Sonetchka supieron la grata noticia. Le aseguro a usted que me
encontraba como transportado al paraíso. Antes no hacía más que
abrumarme con palabrotas como estas: «¡Acuéstate, bruto!» Mas desde
aquel momento andaba de puntillas y hacía callar a los pequeños,
diciéndoles: «¡Chis! ¡Papá viene cansado del trabajo!» Antes de ir a la
oficina me daban café con crema, pero no crea, crema verdadera, ¿eh?
No sé de dónde pudieron sacar el dinero, 11 rublos y 50 kopeks, a fin
de arreglarme la ropa. Lo cierto es que ellas me pulieron de pies a
cabeza; tuve botas, chaleco de magnífico hilo y uniforme, todo en muy
buen uso: les costó 11 rublos y medio. Seis días ha, cuando entregué
íntegros mis honorarios, 23 rublos y 40 kopeks, mi mujer me acarició en
la mejilla, diciéndome: «¡vaya un pez que estás hecho!» Naturalmente,
esto ocurrió cuando estábamos solos. Dígame usted si no es encantador...

Marmeladoff se interrumpió, trató de sonreír; pero súbito temblor agitó
su barba. Dominó, sin embargo, en seguida, su emoción. Raskolnikoff
no sabía qué pensar de aquel borracho, que vagaba al azar desde hacía
cinco días, durmiendo en los barcos de pesca, y, a pesar de todo,
sintiendo por su familia profundo cariño. El joven le escuchaba con
la mayor atención, pero experimentando cierta sensación de malestar.
Estaba enojado consigo mismo por haber entrado en la taberna.

--¡Señor, señor!--dijo el funcionario disculpándose--, quizá halle
usted, como los demás, risible todo lo que le cuento; acaso le estoy
fastidiando refiriéndole estos tontos y miserables pormenores de mi
existencia doméstica; mas para mí no crea usted que son divertidos,
porque le aseguro que siento todas estas cosas... Durante aquel día
maldito hice proyectos encantadores; pensé en el medio de organizar
nuestra vida, de vestir a los niños, de procurar reposo a mi mujer,
de sacar del fango a mi hija única. ¡Oh, cuántos planes formaba!
Pues bien, señor (Marmeladoff empezó a temblar de repente; levantó
la cabeza y miró a la cara a su interlocutor), el mismo día, cinco
hace hoy, después de haber acariciado todos estos sueños, robé, como
un ladrón nocturno, la llave a mi mujer y tomé del baúl todo lo que
quedaba del dinero que yo había llevado. ¿Cuánto había? No lo recuerdo.
Mírenme todos: hace cinco días que abandoné mi casa; no se sabe en
ella qué es de mí; he perdido mi empleo, he dejado mi uniforme en una
taberna y me han dado este traje en su lugar... Todo, todo ha acabado...

Marmeladoff se dió un puñetazo en la frente, rechinó los dientes y
cerrando los ojos se puso de codos en la mesa... Al cabo de un momento
cambió bruscamente la expresión de su rostro, miró a Raskolnikoff con
afectado cinismo y dijo riéndose:

--¡He estado hoy en casa de Sonia; he ido a pedirle dinero para beber!
¡Je, je, je!

--¡Y te lo ha dado!--gritó, riéndose, uno de los parroquianos que
formaba parte del grupo recién llegado a la taberna.

--Con su dinero he pagado esta media botella--repuso Marmeladoff
dirigiéndose exclusivamente a nuestro joven--. Sonia fué a buscar
treinta kopeks y me los entregó; era cuanto tenía; lo he visto con
mis propios ojos. No me dijo nada; se limitó a mirarme en silencio,
una mirada que no pertenece a la tierra, una mirada como deben tener
los ángeles que lloran sobre los pecados de los hombres pero no los
condenan. ¡Qué triste es que no le reprendan a uno! Treinta kopeks,
sí, que de seguro necesitaba. ¿Qué me dice usted, querido señor?
Ahora tiene ella que ir bien arreglada. La elegancia y los afeites,
indispensables en su oficio, cuestan dinero; lo comprenderá usted; hay
que tener pomada, enaguas almidonadas, lindas botitas que hagan bonito
el pie para lucirlo al saltar los charcos. ¿Comprende usted, comprende
usted la importancia de esta limpieza y elegancia? Pues bien, yo,
su padre, según la Naturaleza, ha ido a pedirle esos treinta kopeks
para bebérmelos. ¡Y me los bebo! Ya están bebidos... vamos, ¿quién ha
de tener compasión de un hombre como yo? Ahora, señor, ¿puede usted
compadecerme? Hable usted, señor: ¿tiene usted piedad de mí? ¿Sí o no?
¡Je, je, je!

Iba a servirse nuevamente, pero echó de ver que la media botella estaba
vacía.

--¿Por qué se ha de tener lástima de ti?--gritó el tabernero.

Estallaron risas mezcladas con injurias. Los que no habían oído las
palabras del ex funcionario, formaban coro con los otros, solamente al
ver su catadura.

Marmeladoff, como si no hubiese esperado otra cosa que la interpelación
del tabernero, para soltar el torrente de su elocuencia, se levantó
vivamente y, con el brazo extendido hacia delante, replicó con
exaltación:

--¡Por qué tener compasión de mí! ¡Por qué tener compasión de mí! ¡Es
verdad, no se me debe compadecer! ¡Hay que crucificarme, ponerme en
la cruz, no tenerme lástima! ¡Crucifícame, juez, pero, al hacerlo,
ten piedad de mí! Así iré yo mismo al suplicio, porque no tengo sed
de alegría, sino de dolor y de lágrimas. ¿Piensas tú, tendero, que tu
media botella me ha proporcionado placer? Buscaba la tristeza, tristeza
y lágrimas en el fondo de este frasco, y la he encontrado y saboreado.
Pero Aquel que ha tenido piedad de todos los hombres, Aquel que todo lo
comprende, tendrá piedad de nosotros; El es el único juez, El vendrá
el último día y preguntará: «¿Dónde está la hija que has sacrificado
por una madrastra odiosa y tísica y por niños que no eran sus hermanos?
¿Dónde está la joven que ha tenido piedad terrestre y no ha vuelto con
horror las espaldas a este crapuloso borracho?» Y El dirá entonces:
«Ven, yo te he perdonado una vez... yo te he perdonado ya una vez...
ahora, todos tus pecados te son perdonados, porque has amado mucho...»
Y El perdonará a mi Sonia, la perdonará, yo lo sé, lo he sentido en
mi corazón cuando estaba en su casa.... Todos serán juzgados por El
y El perdonará a todos, a los buenos y a los malos, a los sabios y a
los pacíficos... y cuando haya acabado con ellos, nos tocará la vez
a nosotros. «Acercaos también, nos dirá El; acercaos vosotros los
borrachos, acercaos los cobardes, acercaos los impúdicos», y nos
aproximaremos todos sin temor y El nos dirá: «¡Sois unos cochinos!
¡Tenéis sobre vosotros la marca de la bestia, pero venid también!»
Y los sabios, los inteligentes dirán: «Señor, ¿por qué recibes Tú a
éstos?» Y El responderá: «Yo los recibo ¡oh sabios! porque ninguno de
ellos se ha creído digno de este favor...» Y El nos abrirá los brazos y
nosotros nos precipitaremos en ellos... y nos desharemos en lágrimas...
y comprenderemos... sí, entonces todo será comprendido por todo el
mundo, y Catalina Ivanovna también comprenderá... Señor, vénganos el tu
reino.

Falto de fuerzas, se dejó caer en el banco sin mirar a nadie, como si
desde largo rato se hubiese olvidado del lugar en que se hallaba y de
las personas que le rodeaban, y quedó absorto en la visión de fantasmas
de ultratumba. Sus palabras produjeron cierta impresión; durante un
momento cesó el barullo; pero bien pronto volvieron a estallar las
risas, mezcladas con invectivas:

--¡Muy bien hablado!

--¡Gruñón!

--¡Charlatán!

--¡Burócrata!

--Vámonos, señor--dijo bruscamente Marmeladoff, levantando la cabeza
y dirigiéndose a Raskolnikoff--; condúzcame usted al patio de la casa
Kozel... Ya es tiempo de que vuelva al lado de mi mujer.

Rato hacía ya que el joven deseaba irse y se le había ocurrido ofrecer
el apoyo de su brazo a Marmeladoff. Este último tenía las piernas aun
menos firmes que la voz; de modo que iba casi colgado del brazo de su
compañero. La distancia que tenían que recorrer era de doscientos o
trescientos pasos. A medida que el borracho se acercaba a su domicilio,
parecía más inquieto y preocupado.

--No es precisamente de Catalina Ivanovna de quien tengo yo ahora
miedo--balbuceaba conmovido--. Ya sé que empezará por tirarme de los
cabellos; pero, ¿qué me importa? Me alegro que me tire de ellos. No,
no es eso lo que me espanta; lo que yo temo son sus ojos, sí, sus
ojos... Temo también las manchas rojas de sus mejillas, y me da miedo
además su respiración. ¿Has notado cómo respiran los que padecen esa
enfermedad... cuando experimentan una emoción violenta? Temo las
lágrimas de los chicos... porque si Sonia no les ha llevado algo de
comer, no sé cómo se las habrán arreglado... no lo sé. A los golpes
no les tengo miedo... sabe, en efecto, que, lejos de hacerme sufrir,
esos golpes son un gozo para mí... Casi no puedo pasar sin ello... Sí,
es mejor que me pegue, que alivie de ese modo el corazón... más vale
así; pero he ahí la casa Kozel. El propietario es un cerrajero alemán,
hombre rico... ¡Acompáñeme!...

Después de haber atravesado el patio se pusieron a subir al cuarto
piso. Eran cerca de las once, y, aunque propiamente hablando no había
aún anochecido en San Petersburgo, a medida que subían más obscura
encontraban la escalera; en lo alto la obscuridad era completa.

La puertecilla ahumada que daba al descansillo estaba abierta; un cabo
de vela alumbraba una pobrísima pieza de diez pasos de largo. Esta
pieza, que desde el umbral se veía por completo, estaba en el mayor
desorden. Había por todos lados ropas de niños. Una sábana agujereada,
extendida de manera conveniente, ocultaba uno de los rincones, el
más distante de la puerta; detrás de este biombo improvisado, había,
probablemente, una cama. Todo el mobiliario consistía en dos sillas y
un sofá de gutapercha, que tenía delante una mesa vieja, de madera de
pino, sin barnizar y sin tapete. Encima de la mesa, en un candelero
de hierro se consumía el cabo de vela que medio alumbraba la pieza.
Marmeladoff dormía en el pasillo. La puerta que comunicaba con los
otros cuartos alquilados de Amalia Ludvigovna estaba entreabierta, y
se oía ruido de voces; sin duda, en aquel momento jugaban a cartas y
tomaban te los inquilinos. Se percibían más de lo necesario sus gritos,
sus carcajadas y sus palabras, por extremo libres y atrevidas.

Raskolnikoff reconoció en seguida a Catalina Ivanovna. Era una mujer
flaca, bastante alta y bien formada, pero de aspecto muy enfermizo.
Conservaba aún hermosos cabellos de color castaño y, como había dicho
Marmeladoff, sus mejillas tenían manchas rojizas. Con los labios
secos, oprimíase el pecho con ambas manos, y se paseaba de un lado a
otro de la misérrima habitación. Su respiración era corta y desigual;
los ojos le brillaban febrilmente y tenía la mirada dura e inmóvil.
Iluminada por la luz moribunda del cabo de vela, su rostro de tísica
producía penosa impresión. A Raskolnikoff le pareció que Catalina
Ivanovna no debía tener arriba de treinta años; era, en efecto, mucho
más joven que su marido... No advirtió la llegada de los dos hombres;
parecía que no conservaba la facultad de ver ni la de oír.

Hacía en la habitación un calor sofocante, y subían de la escalera
emanaciones infectas; sin embargo, a Catalina Ivanovna no se le había
ocurrido abrir la ventana, ni cerrar la puerta. La del interior,
solamente entornada, dejaba paso a una espesa humareda de tabaco, que
hacía toser a la enferma; pero ella no se cuidaba de tal cosa.

La niña más pequeña, de seis años, dormía en el suelo con la cabeza
apoyada en el sofá; el varoncito, un año mayor que la pequeñuela,
temblaba llorando en un rincón; probablemente acababan de pegarle. La
mayor, una muchachilla de nueve años, delgada y crecidita, llevaba una
camisa toda rota, y echado sobre los hombros desnudos un viejo _burnus_
señoril que se le debía haber hecho dos años antes, porque al presente
no le llegaba más que hasta las rodillas.

En pie, en un rincón al lado de su hermanito, había pasado el brazo,
largo y delgado como una cerilla, alrededor del cuello del niño y le
hablaba muy quedo, sin duda para hacerle callar. Sus grandes ojos,
obscuros, abiertos por el terror, parecían aún mayores en aquella
carita descarnada. Marmeladoff, en vez de entrar en el aposento, se
arrodilló en la puerta; pero invitó a pasar a Raskolnikoff. La mujer,
al ver un desconocido, se detuvo distraídamente ante él, tratando de
explicarse su presencia. «¿Qué se le ha perdido aquí a ese hombre?»--se
preguntaba. Pero en seguida supuso que el desconocido se dirigía a
casa de algún otro inquilino, puesto que el cuarto de Marmeladoff era
un sitio de paso. Así, pues, desentendiéndose de aquel extraño, se
preparaba a abrir la puerta de comunicación, cuando de repente lanzó un
grito: acababa de ver a su marido de rodillas en el umbral.

--¡Ah! ¿Al fin vuelves?--dijo, con voz en que vibrara la cólera--.
¡Infame! ¡Monstruo! A ver, ¿qué dinero llevas en los bolsillos? ¿Qué
traje es éste? ¿Qué has hecho del tuyo? ¿Qué es del dinero? ¡Habla!

Se apresuró a registrarle. Lejos de oponer resistencia, Marmeladoff
apartó ambos brazos para facilitar el registro de los bolsillos. No
llevaba encima ni un solo kopek.

--¿Dónde está el dinero?--gritaba su esposa--. ¡Oh Dios mío! ¿Es
posible que se lo haya bebido todo? ¡Doce rublos que había en el
cofre!...

Acometida de un acceso de rabia agarró a su marido por los cabellos y
lo arrastró violentamente a la sala. No se desmintió la paciencia de
Marmeladoff: el hombre siguió dócilmente a su mujer arrastrándose de
rodillas tras de ella.

--¡Si me da gusto, si no es un dolor para mí!--gritaba, dirigiéndose
a su acompañante, mientras Catalina Ivanovna le zarandeaba con fuerza
la cabeza; una de las veces le hizo dar con la frente un porrazo en el
suelo.

La niña, que dormía, se despertó, y se echó a llorar. El muchacho,
de pie en uno de los ángulos de la habitación, no pudo soportar
este espectáculo, empezó a temblar y a dar gritos y se lanzó hacia
su hermana; el espanto casi le produjo convulsiones. La niña mayor
temblaba como la hoja en el árbol.

--¡Se lo ha bebido todo; se lo ha bebido todo!--vociferaba Catalina
Ivanovna en el colmo de la desesperación--. ¡Ni siquiera conserva el
traje!... ¡Y tienen hambre, tienen hambre!--repetía retorciéndose
las manos y señalando a los niños--. ¡Oh vida tres veces maldita!
¿Y a usted cómo no le da vergüenza de venir aquí al salir de la
taberna?--añadió volviéndose bruscamente hacia Raskolnikoff--. Has
estado allí bebiendo con él, ¿no es eso? ¿Has estado allí bebiendo con
él?... ¡Vete, vete!...

El joven no esperó a que se lo repitiesen, y se retiraba sin decir
una palabra, en el momento que la puerta interior se abría de par en
par y aparecían en el umbral muchos curiosos de mirada desvergonzada
y burlona. Llevaban todos el gorro y fumaban unos en pipa y otros
cigarrillos. Vestían los unos trajes de dormir, e iban otros tan
ligeros de ropa que rayaba en la indecencia; algunos no habían dejado
los naipes para salir. Lo que más les divertía era oír a Marmeladoff,
arrastrado por los cabellos, gritar que aquello le daba gusto.

Empezaban ya los inquilinos a invadir la habitación, cuando de repente
se oyó una voz irritada; era Amalia Ludvigovna en persona que,
abriéndose paso a través del grupo, venía para restablecer el orden a
su manera. Por centésima vez manifestó a la pobre mujer que tenía que
dejar el cuarto al día siguiente.

Como es de suponer, esta despedida fué dada en términos insultantes.
Raskolnikoff llevaba encima el resto del rublo que había cambiado en la
taberna. Antes de salir tomó del bolsillo un puñado de cobres y, sin
ser visto, puso las monedas en la repisa de la ventana; pero antes de
bajar la escalera se arrepintió de su generosidad, y poco faltó para
que subiese de nuevo a casa de Marmeladoff.

--¡Valiente tontería he hecho!--pensaba--. Ellos cuentan con Sonia,
pero yo no cuento con nadie--. Reflexionó, sin embargo, que no podía
recobrar su dinero y que aunque pudiese, no lo haría. Después de esta
reflexión prosiguió su camino--. Le hace falta pomada a Sonia--continuó
diciéndose con burlona sonrisa, andando ya por la calle--. La elegancia
cuesta dinero... ¡Hum! Según se ve Sonia no ha sido muy afortunada hoy.
La caza del hombre es como la caza de los animales silvestres; se corre
el peligro de volverse uno a casa de vacío. De seguro que mañana lo
pasarían mal sin mi dinero... ¡Ah! ¡Sí, Sonia! ¡La verdad es que han
encontrado en ella buena vaca de leche!... Y se aprovechan bien. Esto
no les preocupaba nada; se han acostumbrado ya a ello. Al principio
lloriquearon un poco; después se han habituado. ¡El hombre es cobarde y
se hace a todo!

Raskolnikoff se quedó pensativo.

--¡Pues bien; si he mentido--exclamó--, si el hombre no es
necesariamente un cobarde, debe atropellar todos los temores y todos
los prejuicios que le detienen!


III

Tarde era cuando al día siguiente se despertó tras de un sueño agitado
que no le devolvió las fuerzas y aumentó, de consiguiente, su mal
humor. Paseó su mirada por el aposento con ojos irritados. Aquel
cuartito, de seis pies de largo, ofrecía un aspecto muy lastimoso con
el empapelado amarillento lleno de polvo y destrozado; además era tan
bajo, que un hombre de elevada estatura corría peligro de chocar con el
techo. El mobiliario estaba en armonía con el local; tres sillas viejas
más o menos desvencijadas; en un rincón, una mesa de madera pintada, en
la cual había libros y cuadernos cubiertos de polvo, prueba evidente de
que no se había puesto mano en ellos durante mucho tiempo, y en fin, un
grande y feísimo sofá, cuya tela estaba hecha pedazos.

Este sofá, que ocupaba casi la mitad de la habitación, servía de
lecho a Raskolnikoff. El joven se acostaba a menudo allí vestido y
sin mantas; se echaba encima, a guisa de colcha, su viejo capote de
estudiante, y convertía en almohada un cojín pequeño, bajo el cual
ponía, para levantarlo, toda su ropa, limpia o sucia. Delante del sofá
había una mesita.

La misantropía de Raskolnikoff armonizaba muy bien con el desaseo de
su tugurio. Sentía tal aversión a todo rostro humano, que solamente el
ver la criada encargada de asear el cuarto la exasperaba. Suele ocurrir
esto a algunos monómanos preocupados por una idea fija.

Quince días hacía que la patrona había cortado los víveres a su pupilo
y a éste no se le había ocurrido tener una explicación con ella.

En cuanto a Anastasia, cocinera y única sirvienta de la casa, no le
molestaba ver al pupilo en aquella disposición de ánimo, puesto que así
éste daba menos que hacer; había cesado por completo de arreglar el
cuarto de Raskolnikoff y de sacudir el polvo. A lo sumo, venía una vez
cada ocho días a dar una escobada. En el momento de entrar la criada el
joven despertó.

--Levántate. ¿Qué te pasa para dormir así? Son las nueve; te traigo te,
¿quieres una taza? ¡Huy qué cara! ¡Pareces un cadáver!

El inquilino abrió los ojos, se desperezó y, reconociendo a Anastasia,
le preguntó, haciendo un penoso esfuerzo para levantarse.

--¿Me lo envía la patrona?

--No hay cuidado que se le ocurra semejante cosa.

La sirvienta colocó delante del joven su propia tetera y puso en la
mesa dos terroncitos de azúcar morena.

--Anastasia, toma este dinero--dijo Raskolnikoff sacando del bolsillo
unas monedas de cobre (también se había acostado vestido)--, y haz el
favor de ir a buscarme un panecillo blanco. Pásate por la salchichería
y tráete un poco de embutido barato.

--En seguida te traeré el panecillo; pero en lugar de salchicha, ¿no
sería mejor que tomases un poco de _chatchi_? Se hizo ayer y está muy
rico. Te guardé un poco... pero como te retiraste tan tarde... Está muy
bueno.

Fué a buscar el _chatchi_, y cuando Raskolnikoff se puso a comer, la
sirvienta se sentó a su lado, en el sofá, y empezó a charlar como lo
que era, como una campesina.

--Praskovia Pavlona quiere dar parte a la policía.

El rostro del joven se alteró.

--¡A la policía! ¿Por qué?

--Porque no le pagas ni quieres irte. Ahí tienes el por qué.

--¡Demonio, no me faltaba más que esto!--dijo entre dientes--. No
podría hacerlo en peor hora para mí... Esa mujer es tonta--añadió en
alta voz--. Iré a verla y le hablaré.

--Como tonta, lo es ella y lo soy yo. Pero tú, que eres inteligente,
¿por qué te estás así tendido como un asno? ¿Cómo es que no tienes
nunca dinero? Según he oído decir, antes dabas lecciones. ¿Por qué
ahora no haces nada?

--Sí que hago--respondió secamente y como a pesar suyo Raskolnikoff.

--¿Qué es lo que haces?

--Cierto trabajo...

--¿Qué trabajo?

--Medito--respondió seriamente después de una pausa.

Anastasia se echó a reír.

Tenía el carácter alegre; pero cuando se reía, era con risa estrepitosa
que sacudía todo su cuerpo y acababa por hacerle daño.

--¿Y el pensar te proporciona mucho dinero?--preguntó cuando pudo
hablar.

--No se puede ir a dar lecciones cuando no tiene uno botas que ponerse.
Además, desprecio ese dinero.

--Quizás algún día te pese.

--Para lo que se gana dando lecciones... ¿Qué se puede hacer con unos
cuantos kopeks?--siguió diciendo con tono agrio y dirigiéndose más bien
a sí mismo que a su interlocutora.

--¿De modo que deseas adquirir de golpe la fortuna?

Raskolnikoff la miró con aire extraño, y guardó silencio durante
algunos momentos.

--Sí, una fortuna--dijo luego con energía.

--¿Sabes que me das miedo? ¡Eres terrible! ¿Voy a buscarte el panecillo?

--Como quieras.

--¡Oh, se me olvidaba! Han traído una carta para ti.

--¡Una carta para mí! ¿De quién?

--No sé de quien; le he dado al cartero tres kopeks de mi bolsillo. He
hecho bien, ¿no es cierto?

--¡Tráela, por amor de Dios, tráela!--exclamó Raskolnikoff muy
agitado--. ¡Señor!

Un minuto después la carta estaba en sus manos.

No se había engañado; era de su madre, y traía el sello del gobierno
de R... Al recibirla, no pudo menos de palidecer; hacía largo tiempo
que no tenía noticias de los suyos; otra cosa, además, le oprimía
violentamente el corazón en aquel momento.

--Anastasia, haz el favor de irte; ahí tienes tus tres kopeks; pero,
¡por amor de Dios!, vete en seguida.

La carta temblaba en sus manos; no quería abrirla en presencia de
Anastasia, y esperó, para comenzar la lectura, a que la criada se
marchase. Cuando se quedó solo, llevó vivamente el papel a sus labios
y lo besó. Después se puso a contemplar atentamente la dirección
reconociendo los caracteres trazados por una mano querida: era la
letra fina e inclinada de su madre, la cual habíale enseñado a leer y
escribir. Vacilaba como si experimentase cierto temor. Al fin rompió el
sobre, la carta era muy larga: dos hojas de papel comercial escritas
por ambos lados.

  «Mi querido Rodia--decíale su madre--. Dos meses ha que no te
  escribo, y esto me hace sufrir hasta el punto de quitarme el sueño.
  Pero, ¿verdad que tú me perdonas mi silencio involuntario? Tú sabes
  cuánto te quiero. Dunia y yo no tenemos a nadie más que a ti en el
  mundo; tú lo eres todo para nosotras, nuestra esperanza, nuestra
  felicidad en el porvenir. No puedes imaginarte lo que he sufrido
  al saber que, al cabo de muchos meses, has tenido que dejar la
  Universidad, por carecer de medios de existencia, y que no tenías
  ni lecciones, ni recursos de ninguna especie.

  »¡Cómo ayudarte con mis ciento veinte rublos de pensión al año!
  Los quince rublos que te mandé hace cuatro meses, se los pedí
  prestados, como sabes, a un comerciante de nuestra ciudad, a
  Anastasio Ivanovitch Vakrutchin. Es un hombre excelente y un amigo
  de tu padre. Pero habiéndole dado poderes para cobrar mi pensión a
  mi nombre, no podía mandarte nada más antes de que se reembolsara
  de lo que me había prestado.

  »Ahora, gracias a Dios, creo que podré enviarte algún dinero;
  por lo demás, me apresuro a decirte que estamos en el caso de
  felicitarnos por nuestra fortuna. En primer lugar, una cosa que
  de seguro te sorprenderá: tu hermana vive conmigo desde hace seis
  semanas y ya no se separará de mi lado. ¡Pobre hija mía! al fin
  acabaron sus tormentos; pero procedamos con orden, pues quiero que
  sepas cómo ha pasado todo y lo que hasta aquí te habíamos ocultado.

  »Hace dos meses me escribías que habías oído hablar de la
  triste situación en que se hallaba Dunia respecto a la familia
  Svidrigailoff y me pedías noticias sobre este asunto. ¿Qué podía
  responderte yo? Si te hubiese puesto al corriente de los hechos,
  lo habrías dejado todo para venir aquí, aunque hubiera sido a
  pie, porque con tu carácter y tus sentimientos no habrías dejado
  que insultasen a tu hermana. Yo estaba desesperada; ¿pero qué
  hacer? Tampoco conocía entonces toda la verdad. Lo malo era que
  Dunetchka[6], que entró el año último como institutriz en esta
  casa, había recibido adelantados cien rublos, que había de pagar
  por medio de un descuento mensual sobre sus honorarios; por esta
  razón ha tenido que desempeñar su cargo hasta la extinción de la
  deuda.

       [6] Diminutivo cariñoso de Dunia.

  »Esta cantidad (ahora puedo ya decírtelo, querido Rodia) se había
  pedido para enviarte los sesenta rublos que tanto necesitabas, y
  que recibiste el año pasado. Te engañamos entonces escribiéndote
  que aquel dinero provenía de antiguas economías reunidas por
  Dunetchka. No era verdad; ahora te lo confieso; porque Dios ha
  permitido que las cosas tomen repentinamente mejor rumbo y también
  para que sepas lo mucho que te quiere Dunia y el hermoso corazón
  que tiene.

  »El hecho es que el señor Svidrigailoff comenzó por mostrarse
  grosero con ella; en la mesa no cesaba de molestarla con
  descortesías y sarcasmos... mas, ¿para qué extenderme en penosos
  pormenores, que no servirían más que para irritarte inútilmente,
  puesto que todo ello ha pasado ya? En suma, aunque tratada con
  muchos miramientos y bondad por Marfa Petrovna, la mujer de
  Svidrigailoff, y por las otras personas de la casa, Dunetchka
  sufría mucho, sobre todo cuando Svidrigailoff, que ha adquirido en
  el regimiento la costumbre de beber, estaba bajo la influencia de
  Baco. Menos mal si todo se hubiera limitado a esto... Pero figúrate
  tú que, bajo apariencias de desprecio hacia tu hermana, este
  insensato ocultaba una verdadera pasión por Dunia.

  »Al fin se quitó la máscara; quiero decir, que hizo a Dunetchka
  proposiciones deshonrosas: trató de seducirla con diversas
  promesas declarándole que estaba dispuesto a abandonar su familia
  e irse a vivir con Dunia en otra ciudad o en el extranjero.
  ¡Figúrate los sufrimientos de tu pobre hermana! No solamente la
  cuestión pecuniaria, de la cual te he hablado, le impedía dejar
  inmediatamente el empleo, sino que además temía, procediendo de
  este modo, despertar las sospechas de Marfa Petrovna e introducir
  la discordia en la familia.

  »El desenlace llegó de improviso. Marfa Petrovna sorprendió
  inopinadamente a su marido en el jardín, en el momento en que
  aquél, con sus instancias, asediaba a Dunia, y entendiendo mal
  la situación, atribuyó todo lo que sucedía a la pobre muchacha.
  Hubo entre ellos una escena terrible. La señora Svidrigailoff
  no quiso avenirse a razones; estuvo gritando durante una hora
  contra su supuesta rival; se olvidó de sí misma, hasta pegarla, y,
  finalmente, la envió a mi casa en la carreta de un campesino, sin
  dejarle tiempo aun para hacer la maleta.

  »Todos los objetos de Dunia, ropa blanca, vestidos, etc., fueron
  metidos revueltos en la telega[7]. Llovía a cántaros, y, después
  de haber sufrido aquellos insultos, tuvo Dunia que caminar diez y
  siete verstas en compañía de un _mujik_[8], en un carro sin toldo.
  Considera ahora qué había de escribirte, en contestación a la
  carta tuya de hace dos meses. Estaba desesperada; no me atrevía
  a decirte la verdad, porque te habría causado una pena hondísima
  e irritado sobremanera. Además, Dunia me lo había prohibido.
  Escribirte para llenar mi carta de futesas, te aseguro que era cosa
  que no me sentía capaz de hacer, teniendo como tenía el corazón
  angustiado. A continuación de este suceso, fuimos durante un mes
  largo la comidilla del pueblo, hasta el extremo de que Dunia y yo
  no podíamos ir a la iglesia sin oír lo que, al pasar nosotras,
  murmuraba la gente con aire despreciativo.

       [7] Carreta de aldeano.

       [8] Campesino siervo.

  »Todo ello por culpa de Marfa Petrovna, la cual había ido difamando
  a Dunia por todas partes. Conocía a mucha gente en el pueblo, y
  durante ese mes venía aquí diariamente. Como además es un poco
  charlatana y le gusta tanto hablar mal de su marido, pronto propaló
  la historia, no sólo por el pueblo, sino por todo el distrito. Mi
  salud no resistió; pero Dunetchka se mostró más fuerte: lejos de
  abatirse ante la calumnia, ella era quien me consolaba esforzándose
  en darme valor. ¡Si la hubieses visto! ¡Es un ángel!

  »La misericordia divina ha puesto fin a nuestros infortunios. El
  señor Svidrigailoff reflexionó, sin duda, y compadecido de la
  joven a quien hubo antes de comprometer, puso ante los ojos de
  Marfa Petrovna pruebas convincentes de la inocencia de Dunia.
  Svidrigailoff conservaba una carta que, antes de la escena del
  jardín, mi hija se vió obligada a escribirle, rehusándole una cita
  que él le había pedido. En esta carta Dunia le echaba en cara la
  indignidad de su conducta respecto a su mujer, le recordaba sus
  deberes de padre y esposo y, por último, le hacía ver la vileza de
  perseguir a una joven desgraciada y sin defensa.

  »Con esto no le quedó duda alguna a Marfa Petrovna de la inocencia
  de Dunetchka. Al día siguiente, que era domingo, vino a nuestra
  casa, y después de contárselo todo, abrazó a Dunia y le pidió
  perdón llorando. Después recorrió el pueblo, casa por casa, y en
  todas partes rindió espléndido homenaje a la honradez de Dunetchka
  y a la nobleza de sus sentimientos y conducta. No contentándose
  con esto, enseñaba a todo el mundo y leía en alta voz la carta
  autógrafa de Dunia a Svidrigailoff; hizo además sacar de ella
  muchas copias (lo que ya me parece excesivo). Como ves, ha
  rehabilitado por completo a Dunetchka, mientras el marido de Marfa
  Petrovna sale de esta aventura cubierto de imborrable deshonor. No
  puedo menos de compadecer a ese loco, tan severamente castigado.

  »Has de saber, Rodia, que se ha presentado para tu hermana un
  partido, y que ella ha dado su consentimiento, cosa que me
  apresuro a comunicarte. Tú nos perdonarás a Dunia y a mí el haber
  tomado esta resolución sin consultarte, cuando sepas que el asunto
  no admitía dilaciones y que era imposible esperar, para responder,
  a que tú nos contestaras. Por otra parte, no estando aquí, no
  podías juzgar con conocimiento de causa.
 """

# -----------------------------------------------------------------------------
# Unigrama
# -----------------------------------------------------------------------------
class ModeloUnigrama:
    """
    Modelo de lenguaje Unigrama: P(w) = conteo(w) / total
    """
    def __init__(self):
        self.conteos = Counter()
        self.total = 0
        self.vocab = set()

    def entrenar(self, corpus: str) -> None:
        palabras = extraer_palabras(corpus)
        self.conteos = Counter(palabras)
        self.total = len(palabras)
        self.vocab = set(palabras)

    def prob(self, w: str) -> float:
        if self.total == 0:
            return 0.0
        return self.conteos[w] / self.total

    def generar(self, longitud: int = 10) -> List[str]:
        if not self.conteos:
            return []
        palabras = list(self.conteos.keys())
        pesos = [self.conteos[w] / self.total for w in palabras]
        salida = []
        for _ in range(longitud):
            salida.append(random.choices(palabras, weights=pesos)[0])
        return salida

# -----------------------------------------------------------------------------
# Bigrama (equivale a Markov de orden 1)
# -----------------------------------------------------------------------------
class ModeloBigrama:
    """
    Modelo de Bigramas: P(w_i | w_{i-1}) = conteo(w_{i-1}, w_i) / conteo(w_{i-1})
    """
    def __init__(self):
        self.bigramas = Counter()
        self.unigramas = Counter()
        self.vocab = set()
        self.inicios = []  # palabras posibles de inicio

    def entrenar(self, corpus: str) -> None:
        pal = extraer_palabras(corpus)
        self.vocab = set(pal)
        self.unigramas = Counter(pal)
        for i in range(len(pal)-1):
            self.bigramas[(pal[i], pal[i+1])] += 1
        self.inicios = list(self.vocab)

    def dist_siguiente(self, contexto: str) -> Dict[str, float]:
        if contexto not in self.unigramas:
            return {}
        base = self.unigramas[contexto]
        dist = {}
        for (w0, w1), cnt in self.bigramas.items():
            if w0 == contexto:
                dist[w1] = cnt / base
        return dist

    def generar(self, palabra_inicio: Optional[str] = None, longitud: int = 10) -> List[str]:
        if not self.unigramas:
            return []
        if palabra_inicio is None:
            actual = random.choice(self.inicios) if self.inicios else random.choice(list(self.vocab))
        else:
            actual = palabra_inicio.lower()
            if actual not in self.vocab:
                return []
        salida = [actual]
        for _ in range(longitud-1):
            dist = self.dist_siguiente(actual)
            if not dist:
                break
            palabras = list(dist.keys())
            pesos = list(dist.values())
            nxt = random.choices(palabras, weights=pesos)[0]
            salida.append(nxt)
            actual = nxt
        return salida

# -----------------------------------------------------------------------------
# Cadena de Markov de orden k (generaliza n-gramas)
# -----------------------------------------------------------------------------
class CadenaMarkov:
    """
    Cadena de Markov de orden k (k >= 1), con tokens <START> y <END>.
    Estado = tupla de k tokens previos.
    """
    def __init__(self, orden: int = 2):
        self.orden = max(1, int(orden))
        self.transiciones = defaultdict(Counter)  # estado -> Counter(siguiente)
        self.estados = set()

    def entrenar(self, corpus: str) -> None:
        pal = extraer_palabras(corpus)
        proc = list(tok_start(self.orden)) + pal + ["<END>"]
        self.transiciones.clear()
        self.estados.clear()
        for i in range(len(proc) - self.orden):
            estado = tuple(proc[i:i+self.orden])
            nxt = proc[i+self.orden]
            self.transiciones[estado][nxt] += 1
            self.estados.add(estado)

    def dist_siguiente(self, estado: Tuple[str, ...]) -> Dict[str, float]:
        if estado not in self.transiciones:
            return {}
        total = sum(self.transiciones[estado].values())
        if total == 0:
            return {}
        return {w: c/total for w, c in self.transiciones[estado].items()}

    def generar(self, max_tokens: int = 30) -> List[str]:
        estado = tok_start(self.orden)
        salida = []
        for _ in range(max_tokens):
            dist = self.dist_siguiente(estado)
            if not dist:
                break
            palabras = list(dist.keys())
            pesos = list(dist.values())
            nxt = random.choices(palabras, weights=pesos)[0]
            if nxt == "<END>":
                break
            salida.append(nxt)
            estado = (*estado[1:], nxt)
        return salida

    # Ayuda para simulación paso a paso (UI)
    def paso(self, estado: Tuple[str, ...]) -> Tuple[Tuple[str, ...], Optional[str]]:
        """Devuelve (nuevo_estado, token_elegido | None)"""
        dist = self.dist_siguiente(estado)
        if not dist:
            return (estado, None)
        palabras = list(dist.keys())
        pesos = list(dist.values())
        nxt = random.choices(palabras, weights=pesos)[0]
        if nxt == "<END>":
            return (estado, "<END>")
        nuevo = (*estado[1:], nxt)
        return (nuevo, nxt)

# -----------------------------------------------------------------------------
# Demo CLI 
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("Demo Markov (orden=2) — generar 30 tokens")
    m = CadenaMarkov(orden=2)
    m.entrenar(ai_corpus)
    salida = m.generar(30)
    print(">>", " ".join(salida))
