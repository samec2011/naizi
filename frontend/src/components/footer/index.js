import styles from './style.module.css'
import { Container, LinkComponent } from '../index'
import MyImage from './logo_footer.png';

const Footer = () => {
  return <footer className={styles.footer}>
      <Container className={styles.footer__container}>
        <img src={MyImage} alt="logo" />
        <LinkComponent href='#' title='На-изи' className={styles.footer__brand} />
      </Container>
  </footer>
}

export default Footer
