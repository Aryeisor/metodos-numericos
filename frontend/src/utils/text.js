/** Minúsculas y sin tildes: «Diferenciación» y «diferenciacion» son iguales. */
export const fold = (text) => text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
