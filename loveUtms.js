
setUrlParameters();

async function setUrlParameters() {
    const urlParameters = getUrlParameters();
    const elements = document.getElementsByClassName('love-link');

    for (let i = 0; i < elements.length; i++) {
        const element = elements[i];
        if (element.hasAttribute('href')) {
            const currentHref = element.getAttribute('href');
            const updatedHref = modifyUrl(currentHref, urlParameters);
            element.setAttribute('href', updatedHref);
        }
        else if (element.hasAttribute('data-href')) {
            const currentDataHref = element.getAttribute('data-href');
            const updatedDataHref = modifyUrl(currentDataHref, urlParameters);
            element.setAttribute('data-href', updatedDataHref);
        }
    }

}

function modifyUrl(url, queryStrings) {
  return url + queryStrings;
}

function getUrlParameters() {
    const currentUrl = window.location.href;
    const url = new URL(currentUrl);
    return url.search;
}
